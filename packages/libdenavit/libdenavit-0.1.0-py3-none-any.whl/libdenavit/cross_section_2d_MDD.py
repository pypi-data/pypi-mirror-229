from math import pi, sin
from libdenavit import find_limit_point_in_list, interpolate_list
from libdenavit.OpenSees import AnalysisResults
import openseespy.opensees as ops
import numpy as np
import warnings


class CrossSection2d:
    def __init__(self, section, axis=None):
        # Physical parameters
        self.section = section
        self.axis = axis

    def build_ops_model(self, section_id, section_args, section_kwargs):
        ops.wipe()
        ops.model('basic', '-ndm', 2, '-ndf', 3)

        ops.node(1, 0, 0)
        ops.node(2, 0, 0)

        ops.fix(1, 1, 1, 1)
        ops.fix(2, 0, 1, 0)

        ops.mass(2, 1, 1, 1)

        if type(self.section).__name__ == "RC":
            self.section.build_ops_fiber_section(section_id, *section_args, **section_kwargs, axis=self.axis)
        else:
            raise ValueError(f'Unknown cross section type {type(self.section).__name__}')

        ops.element('zeroLengthSection', 1, 1, 2, section_id)

    def run_ops_analysis(self, analysis_type, section_args, section_kwargs, e=0, P=0, num_steps_vertical=20,
                         load_incr_factor=1e-3, disp_incr_factor=1e-7,
                         eigenvalue_limit=0,
                         percent_load_drop_limit=0.05,
                         concrete_strain_limit=-0.01,
                         steel_strain_limit=0.05,
                         try_smaller_steps=True,
                         print_limit_point=True):
        """
        Run an OpenSees analysis of the section.

        Parameters
        ----------
        analysis_type : str
            The type of analysis to run, options are
                - 'proportional_limit_point'
                - 'nonproportional_limit_point'
                - 'proportional_target_force' (not yet implemented)
                - 'nonproportional_target_force' (not yet implemented)
                - 'proportional_target_disp' (not yet implemented)
                - 'nonproportional_target_disp' (not yet implemented)
        section_args : list or tuple
            Non-keyworded arguments for the section's build_ops_fiber_section.
        section_kwargs : dict
            Keyworded arguments for the section's build_ops_fiber_section.

        Loading Notes
        -------------
        - The axial load applied to the section is P = LFV.
        - The moment applied to the section is M = LFH.
        - For proportional analyses, LFV and LFH are increased simultaneously
          with a ratio of e (P is ignored).
        - For non-proportional analyses, LFV is increased to P first then held
          constant, then LFH is increased (e is ignored).
        """

        self.build_ops_model(1, section_args, section_kwargs)

        # Initialize analysis results
        results = AnalysisResults()
        attributes = ['applied_axial_load', 'maximum_abs_moment', 'lowest_eigenvalue',
                      'extreme_comp_strain', 'maximum_concrete_compression_strain', 'maximum_steel_strain']
        for attr in attributes:
            setattr(results, attr, [])

        # Define function to find limit point
        def find_limit_point():
            if print_limit_point:
                print(results.exit_message)

            if 'Analysis Failed' in results.exit_message:
                ind, x = find_limit_point_in_list(results.maximum_abs_moment, max(results.maximum_abs_moment))
                warnings.warn(f'Analysis failed')
            elif 'Eigenvalue Limit' in results.exit_message:
                ind, x = find_limit_point_in_list(results.lowest_eigenvalue, eigenvalue_limit)
            elif 'Extreme Compressive Concrete Fiber Strain Limit Reached' in results.exit_message:
                ind, x = find_limit_point_in_list(results.maximum_concrete_compression_strain, concrete_strain_limit)
            elif 'Extreme Steel Fiber Strain Limit Reached' in results.exit_message:
                ind, x = find_limit_point_in_list(results.maximum_steel_strain, steel_strain_limit)
            elif 'Load Drop Limit Reached' in results.exit_message:
                ind, x = find_limit_point_in_list(results.maximum_abs_moment, max(results.maximum_abs_moment))
            else:
                raise Exception('Unknown limit point')

            results.applied_axial_load_at_limit_point = interpolate_list(results.applied_axial_load, ind, x)
            results.maximum_abs_moment_at_limit_point = interpolate_list(results.maximum_abs_moment, ind, x)

        # Run analysis
        if analysis_type.lower() == 'proportional_limit_point':
            basic_load_increment = self.section.p0 * load_incr_factor

            # time = LFV
            ops.timeSeries('Linear', 1)
            ops.pattern('Plain', 1, 1)
            ops.load(2, -1, 0, e)
            ops.integrator('LoadControl', basic_load_increment)
            ops.system('SparseGeneral', '-piv')
            ops.test('NormUnbalance', 1e-3, 10)
            ops.numberer('Plain')
            ops.constraints('Plain')
            ops.algorithm('Newton')
            ops.analysis('Static')
            ops.analyze(1)

            # Define recorder
            def record():
                time = ops.getTime()
                results.applied_axial_load.append(time)
                results.maximum_abs_moment.append(abs(ops.eleForce(1, 3)))
                results.lowest_eigenvalue.append(ops.eigen("-fullGenLapack", 1)[0])
                axial_strain = ops.nodeDisp(2, 1)
                curvature = ops.nodeDisp(2, 3)
                if self.axis == 'x':
                    curvatureX = ops.nodeDisp(2, 3)
                    curvatureY = 0
                elif self.axis == 'y':
                    curvatureX = 0
                    curvatureY = ops.nodeDisp(2, 3)
                else:
                    raise ValueError(f'axis {self.axis} not supported')
                results.maximum_concrete_compression_strain.append(
                    self.section.maximum_concrete_compression_strain(axial_strain, curvatureX, curvatureY))
                results.maximum_steel_strain.append(
                    self.section.maximum_tensile_steel_strain(axial_strain, curvatureX, curvatureY))

            record()

            maximum_applied_axial_load = 0.
            while True:
                ok = ops.analyze(1)
                if try_smaller_steps:
                    if ok != 0:
                        ops.integrator('LoadControl', basic_load_increment / 10)
                        ok = ops.analyze(1)

                    if ok != 0:
                        ops.integrator('LoadControl', basic_load_increment / 100)
                        ok = ops.analyze(1)

                    if ok != 0:
                        ops.integrator('LoadControl', basic_load_increment / 1000)
                        ok = ops.analyze(1)
                        if ok == 0:
                            basic_load_increment = basic_load_increment / 10
                            print(f'Changed the step size to: {basic_load_increment}')

                    if ok != 0:
                        ops.integrator('LoadControl', basic_load_increment / 10000)
                        ok = ops.analyze(1)
                        if ok == 0:
                            basic_load_increment = basic_load_increment / 10
                            print(f'Changed the step size to: {basic_load_increment}')

                if ok != 0:
                    print('Trying ModifiedNewton')
                    ops.algorithm('ModifiedNewton')
                    ok = ops.analyze(1)

                if ok != 0:
                    print('Trying KrylovNewton')
                    ops.algorithm('KrylovNewton')
                    ok = ops.analyze(1)

                if ok != 0:
                    print('Trying KrylovNewton and Greater Tolerance')
                    ops.algorithm('KrylovNewton')
                    ops.test('NormUnbalance', 1e-2, 10)
                    ok = ops.analyze(1)

                if ok == 0:
                    # Reset analysis options
                    ops.algorithm('Newton')
                    ops.test('NormUnbalance', 1e-3, 10)
                    ops.integrator('LoadControl', basic_load_increment)
                else:
                    results.exit_message = 'Analysis Failed'
                    break

                record()

                # Check for drop in applied load
                if percent_load_drop_limit is not None:
                    current_applied_axial_load = results.applied_axial_load[-1]
                    maximum_applied_axial_load = max(maximum_applied_axial_load, current_applied_axial_load)
                    if current_applied_axial_load < (1 - percent_load_drop_limit) * maximum_applied_axial_load:
                        results.exit_message = 'Load Drop Limit Reached'
                        break

                # Check for lowest eigenvalue less than zero
                if eigenvalue_limit is not None:
                    if results.lowest_eigenvalue[-1] < eigenvalue_limit:
                        results.exit_message = 'Eigenvalue Limit Reached'
                        break

                # Check for strain in extreme compressive concrete fiber
                if concrete_strain_limit is not None:
                    if results.maximum_concrete_compression_strain[-1] < concrete_strain_limit:
                        results.exit_message = 'Extreme Compressive Concrete Fiber Strain Limit Reached'
                        break

                # Check for strain in extreme steel fiber
                if steel_strain_limit is not None:
                    if results.maximum_steel_strain[-1] > steel_strain_limit:
                        results.exit_message = 'Extreme Steel Fiber Strain Limit Reached'
                        break

            find_limit_point()
            return results

        elif analysis_type.lower() == 'nonproportional_limit_point':
            basic_curvature_incr = disp_incr_factor / self.section.depth(self.axis)
        
            # region Run vertical load (time = LFV)
            ops.timeSeries('Linear', 100)
            ops.pattern('Plain', 200, 100)
            ops.load(2, -1, 0, 0)
            ops.constraints('Plain')
            ops.numberer('RCM')
            ops.system('UmfPack')
            ops.test('NormUnbalance', 1e-3, 10)
            ops.algorithm('Newton')
            ops.integrator('LoadControl', P / num_steps_vertical)
            ops.analysis('Static')

            # region Define recorder
            def record():
                time = ops.getTime()
                results.applied_axial_load.append(time)
                results.maximum_abs_moment.append(abs(ops.eleForce(1, 3)))
                results.lowest_eigenvalue.append(ops.eigen("-fullGenLapack", 1)[0])
                axial_strain = ops.nodeDisp(2, 1)
                curvature = ops.nodeDisp(2, 3)
                if self.axis == 'x':
                    curvatureX = ops.nodeDisp(2, 3)
                    curvatureY = 0
                elif self.axis == 'y':
                    curvatureX = 0
                    curvatureY = ops.nodeDisp(2, 3)
                else:
                    raise ValueError(f'axis {self.axis} not supported')
                results.maximum_concrete_compression_strain.append(
                    self.section.maximum_concrete_compression_strain(axial_strain, curvatureX, curvatureY))
                results.maximum_steel_strain.append(
                    self.section.maximum_tensile_steel_strain(axial_strain, curvatureX, curvatureY))
            # endregion

            record()

            for i in range(num_steps_vertical):
                ok = ops.analyze(1)

                if ok != 0:
                    results.exit_message = 'Analysis Failed In Vertical Loading'
                    return results

                record()

            # endregion Run vertical load (time = LFV)

            # Run lateral load (time = LFH)
            ops.loadConst('-time', 0.0)
            ops.timeSeries('Linear', 101)
            ops.pattern('Plain', 201, 101)
            ops.load(2, 0, 0, 1)
            ops.integrator('DisplacementControl', 2, 3, basic_curvature_incr)
            ops.analysis('Static')

            # region Define recorder

            def record():
                time = ops.getTime()
                results.applied_axial_load.append(P)
                results.maximum_abs_moment.append(abs(ops.eleForce(1, 3)))
                results.lowest_eigenvalue.append(ops.eigen("-fullGenLapack", 1)[0])
                axial_strain = ops.nodeDisp(2, 1)
                if self.axis == 'x':
                    curvatureX = ops.nodeDisp(2, 3)
                    curvatureY = 0
                elif self.axis == 'y':
                    curvatureX = 0
                    curvatureY = ops.nodeDisp(2, 3)
                else:
                    raise ValueError(f'axis {self.axis} not supported')
                results.maximum_concrete_compression_strain.append(
                    self.section.maximum_concrete_compression_strain(axial_strain, curvatureX, curvatureY))
                results.maximum_steel_strain.append(
                    self.section.maximum_tensile_steel_strain(axial_strain, curvatureX, curvatureY))

            # endregion

            record()

            maximum_time = 0

            while True:
                ok = ops.analyze(1)
                if try_smaller_steps:
                    if ok != 0:
                        print(f'Trying the step size of: {basic_curvature_incr / 10}')
                        ops.integrator('DisplacementControl', 1, 3, basic_curvature_incr / 10)
                        ok = ops.analyze(1)

                    if ok != 0:
                        print(f'Trying the step size of: {basic_curvature_incr / 100}')
                        ops.integrator('DisplacementControl', 1, 3, basic_curvature_incr / 100)
                        ok = ops.analyze(1)

                    if ok != 0:
                        print(f'Trying the step size of: {basic_curvature_incr / 1000}')
                        ops.integrator('DisplacementControl', 1, 3, basic_curvature_incr / 1000)
                        ok = ops.analyze(1)
                        if ok == 0:
                            basic_curvature_incr = basic_curvature_incr / 10
                            print(f'Changed the step size to: {basic_curvature_incr}')

                    if ok != 0:
                        print(f'Trying the step size of: {basic_curvature_incr / 10000}')
                        ops.integrator('DisplacementControl', 1, 3, basic_curvature_incr / 10000)
                        ok = ops.analyze(1)
                        if ok == 0:
                            basic_curvature_incr = basic_curvature_incr / 10
                            print(f'Changed the step size to: {basic_curvature_incr / 10}')

                if ok != 0:
                    print('Trying ModifiedNewton')
                    ops.algorithm('ModifiedNewton')
                    ok = ops.analyze(1)
                    if ok == 0:
                        print('ModifiedNewton worked')

                if ok != 0:
                    print('Trying KrylovNewton')
                    ops.algorithm('KrylovNewton')
                    ok = ops.analyze(1)
                    if ok == 0:
                        print('KrylovNewton worked')

                if ok != 0:
                    print('Trying KrylovNewton and Greater Tolerance')
                    ops.algorithm('KrylovNewton')
                    ops.test('NormUnbalance', 1e-4, 10)
                    ok = ops.analyze(1)
                    if ok == 0:
                        print('KrylovNewton worked')

                if ok == 0:
                    # Reset analysis options
                    ops.algorithm('Newton')
                    ops.test('NormUnbalance', 1e-3, 10)
                    ops.integrator('DisplacementControl', 2, 3, basic_curvature_incr)
                else:
                    results.exit_message = 'Analysis Failed'
                    break

                record()

                # Check for drop in applied load (time = the horizontal load factor)
                if percent_load_drop_limit is not None:
                    current_time = ops.getTime()
                    maximum_time = max(maximum_time, current_time)
                    if current_time < (1 - percent_load_drop_limit) * maximum_time:
                        results.exit_message = 'Load Drop Limit Reached'
                        break

                # Check for lowest eigenvalue less than zero
                if eigenvalue_limit is not None:
                    if results.lowest_eigenvalue[-1] < 0:
                        results.exit_message = 'Eigenvalue Limit Reached'
                        break

                # Check for strain in extreme compressive concrete fiber
                if concrete_strain_limit is not None:
                    if results.maximum_concrete_compression_strain[-1] < concrete_strain_limit:
                        results.exit_message = 'Extreme Compressive Concrete Fiber Strain Limit Reached'
                        break

                # Check for strain in extreme steel fiber
                if steel_strain_limit is not None:
                    if results.maximum_steel_strain[-1] > steel_strain_limit:
                        results.exit_message = 'Extreme Steel Fiber Strain Limit Reached'
                        break

            find_limit_point()
            return results

        else:
            raise ValueError(f'Analysis type {analysis_type} not implemented')

    def run_ops_interaction(self, section_args, section_kwargs, num_points=10, 
                            prop_load_incr_factor=1e-3, nonprop_disp_incr_factor=1e-4):

        # Run one axial load only analysis to determine maximum axial strength
        print("Running cross-section axial only analysis...")
        results = self.run_ops_analysis('proportional_limit_point', section_args, section_kwargs,
                                        load_incr_factor=prop_load_incr_factor)
        print("Axial only analysis is completed.")
        P = [max(results.applied_axial_load)]
        M = [0]
        exit_message = [results.exit_message]
        if P in [None, [None]]:
            raise ValueError('Analysis failed at axial only loading')

        # Loop axial linearly spaced axial loads with non-proportional analyses
        print("Running cross-section non-proportional analysis...")
        for i in range(1, num_points):
            iP = P[0] * (num_points - 1 - i) / (num_points - 1)
            results = self.run_ops_analysis('nonproportional_limit_point', section_args, section_kwargs, P=iP,
                                            disp_incr_factor=nonprop_disp_incr_factor)
            P.append(iP)
            M.append(max(results.maximum_abs_moment))
            exit_message.append(results.exit_message)
        print("Non-proportional analysis is completed.")

        return {'P': P, "M1": M, 'M2': M, 'exit_message': exit_message}

    def run_AASHTO_interaction(self, section_factored=True):
        P, M, et = self.section.section_interaction_2d(self.axis, 100, factored=section_factored)
        return {'P': P, 'M1': M, 'M2': M}
