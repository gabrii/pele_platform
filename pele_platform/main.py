import matplotlib
matplotlib.use("Agg")
import sys
import pele_platform.constants.constants as cs
sys.path.append(cs.DIR)
from argparse import HelpFormatter
from operator import attrgetter
import argparse
import os
import pele_platform.MSM.main as msm
import pele_platform.Rescore.main as gl
import pele_platform.Rescore.simulation as ad


class Launcher():


    def __init__(self, arguments):
        self.cpus = arguments.cpus
        self.software = arguments.software
        self.restart = arguments.restart
        self.test = arguments.test
        self._args = arguments

    def launch(self):
        if self._args.software == "msm":
            if(self._args.clust > self.cpus and self.restart != "msm" and not self.test):
                raise ValueError(cs.CLUSTER_ERROR.format(self.cpus, self._args.clust))
            else:
                msm.run(self._args)
                

        elif self.software == "adaptive":
            ad.run_adaptive(self._args)

        elif self.software in ["glide", "induce_fit"]:
            gl.run(self._args)

        elif self.software == "frag":
            main = os.path.join(cs.DIR, "LigandGrowing/grow.py")
            "{} {} -cp {} -fp {} -ca {} -fa {}".format(cs.PYTHON3, main, self._args.system, self._args.frag, self._args.ca, self._args.fa)

class SortingHelpFormatter(HelpFormatter):
    def add_arguments(self, actions):
        actions = sorted(actions, key=attrgetter('option_strings'))
        super(SortingHelpFormatter, self).add_arguments(actions)

def parseargs(args=[]):
    parser = argparse.ArgumentParser(description='Run PELE Platform', formatter_class=SortingHelpFormatter)
    parser.add_argument('system', type=str, help='complex to run pele on')
    parser.add_argument('residue', type=str, help='residue of the ligand to extract', default=cs.LIG_RES)
    parser.add_argument('chain', type=str, help='chain of the ligand to extract', default=cs.LIG_CHAIN)
    parser.add_argument("--test", action='store_true', help="Run a fast pele_platform test")

    #Pele info
    pele_info = parser.add_argument_group('\nPele Parameters') 
    pele_info.add_argument("--pele", type=str,  help="Pele control_file", default=None)
    pele_info.add_argument('--forcefield', '-f', type=str, help='chain of the ligand to extract', default=cs.FORCEFIELD)
    pele_info.add_argument("--anm_freq", type=int,  help="Frequency to perform ANM", default=4)
    pele_info.add_argument("--sidechain_freq", type=int,  help="Frequency to perform sidechain sampling", default=2)
    pele_info.add_argument("--min_freq", type=int,  help="Frequency to perform all atoms minimization", default=1)
    pele_info.add_argument("--temperature", type=int,  help="Temperature to perform PELE simulation", default=1500)
    pele_info.add_argument("--sidechain_resolution", type=int,  help="Every how many degrees the sidechains will be rotated [10, 30...]", default=10)
    pele_info.add_argument("--steric_trials", type=int,  help="Number fo steric trials on sidechain sampling", default=None)
    pele_info.add_argument("--overlap_factor", type=float,  help="Relaxation of vanderwals clashes from 0 to 1", default=None)
    pele_info.add_argument('--solvent', type=str, help='Type of implicit solvent (OBC/VDGBNP). default [OBC]. i.e. --solvent VDGBNP', default="VDGBNP")

    # Adaptive info
    adaptive_info = parser.add_argument_group('\nAdaptive Parameters') 
    adaptive_info.add_argument("--usesrun", action="store_true",  help="Use srun option with intel")
    adaptive_info.add_argument("--iterations", type=int,  help="PELE iterations", default=50)
    adaptive_info.add_argument("--pele_steps", type=int,  help="PELE steps", default=None)
    adaptive_info.add_argument("--spawning", type=str,  help="Adaptive Spawning type. [epsilon, inverselyProportional]", default=None)
    adaptive_info.add_argument("--density", type=str,  help="Adaptive Density type. [null, continuous]", default=None)
    adaptive_info.add_argument("--cluster_values", type=str,  help="Cluster values", default=None)
    adaptive_info.add_argument("--cluster_conditions", type=str,  help="Cluster conditions", default=None)
    adaptive_info.add_argument("--simulation_type", type=str,  help="Type of simulation [pele, md]", default=None)
    adaptive_info.add_argument('--cpus', type=int, help='number of processors', default=cs.CPUS)
    adaptive_info.add_argument("--equilibration", action="store_true",  help="Whether to do a initial equilibration or not")
    adaptive_info.add_argument("--eq_steps", type=float,  help="Number of equilibration steps", default=cs.EQ_STEPS)
    adaptive_info.add_argument("--adaptive_restart", action="store_true",  help="Whether to set restart true to adaptive")
    adaptive_info.add_argument('--input', nargs="+", help='Set initial input for simulation')
    adaptive_info.add_argument('--report_name', type=str, help='Name of the output report files. i.e. report_Sim1_. Default [report]', default="report")
    adaptive_info.add_argument('--traj_name', type=str, help='Name of the trajectory files (pdb and xtc supported). i.e. trajectory_sim1.pdb. Default [trajectory.xtc]', default="trajectory.xtc")
    adaptive_info.add_argument("--adaptive", type=str,  help="Adaptive control_file", default=None)

    adaptive_info.add_argument("--epsilon", type=float,  help="From 0 to 1 how bias do you want the simulation", default=None)
    adaptive_info.add_argument("--bias_column", type=int,  help="Column of the report starting by 1 towards where to bias simulation", default=None)



    #Ligand Parametrization
    plop_info = parser.add_argument_group('\nLigand Parametrization') 
    plop_info.add_argument("--gridres", type=str, help="Rotamers angle resolution", default=cs.GRIDRES)
    plop_info.add_argument("--core", type=int, help="Give one atom of the core section", default=-1)
    plop_info.add_argument("--mtor", type=int, help="Gives the maximum number of torsions allowed in each group.  Will freeze bonds to extend the core if necessary.", default=4)
    plop_info.add_argument("--n", type=int, help="Maximum Number of Entries in Rotamer File", default=1000)
    plop_info.add_argument("--template", type=str,  help="External template for ligand", default=None)
    plop_info.add_argument("--rotamers", type=str,  help="External romtamers library for ligand", default=None)
    plop_info.add_argument("--mae_lig", type=str, help="ligand .mae file to include QM charges coming from jaguar")

    #PDB preparation info
    receptor_preparation = parser.add_argument_group('\nReceptor Preparation') 
    receptor_preparation.add_argument("--no_ppp", action="store_true",  help="Do not run experimental PPP")
    receptor_preparation.add_argument("--gaps_ter", help="Include TER when a possible gap is found", action='store_true')
    receptor_preparation.add_argument("--charge_ter", help="Charge protein terminals", action='store_true')
    receptor_preparation.add_argument("--skip_prep", action="store_true",  help="Whether to do the initial preprocessing or not")
    receptor_preparation.add_argument("--nonstandard", nargs="+",  help="Mid Chain non standard residues to be treated as ATOM not HETATOM", default = [])
    receptor_preparation.add_argument("--prepwizard", action="store_true",  help="Run protein preparation wizard from schrodinger")


    #Box info
    box_info = parser.add_argument_group('\nBox') 
    box_info.add_argument("--box", type=str, help="Exploration box for Pele")
    box_info.add_argument("--user_center", "-c", nargs='+', type=str, help='center of the box', default=None)
    box_info.add_argument("--box_radius", "-r", type=float,  help="Radius of the box", default=None)

    #Metrics info
    metrics_info = parser.add_argument_group('\nMetrics') 
    metrics_info.add_argument('--native', type=str, help='native file to compare RMSD to', default="")
    metrics_info.add_argument("--atom_dist", nargs="+",  help="Number of the atoms to calculate the distance in between i.e --atom dist 123 456 122 121", default=None)

    #Output info
    output_info = parser.add_argument_group('\nOutput info') 
    output_info.add_argument("--folder", "-wf", type=str,  help="Name of the output working folder", default=None)
    output_info.add_argument("--output", "-o", type=str,  help="Name of the adaptive output", default="output")

    #Full simulation
    full_info = parser.add_argument_group('\nFull Simulation') 
    full_info.add_argument('--randomize', action="store_true", help='Randomize ligand position around protein')
    full_info.add_argument("--full", action="store_true",  help="Launch ful ful binding site exploration")
    full_info.add_argument("--poses", type=int,  help="Number of ligand poses for global exploration", default=40)

    #Kinase simulation
    kinase_info = parser.add_argument_group('\nFull Simulation') 
    kinase_info.add_argument("--hbond", nargs='+',  help="Definition of kinase hbond", default= [None, None] )
    kinase_info.add_argument("--precision_glide", type=str,  help="Glide precision.. Options = [SP, XP]", default="SP")

    #MSM simulation
    msm_info = parser.add_argument_group('\nMSM Simulation') 
    msm_info.add_argument("--msm", action="store_true",  help="Launch MSM")
    msm_info.add_argument("--clust", type=int, help="Numbers of clusters to start PELE's exploration with", default=cs.CLUSTERS)
    msm_info.add_argument("--restart", type=str, help="Restart the platform from [all, pele, msm] with these keywords", default=cs.PLATFORM_RESTART)
    msm_info.add_argument("--precision", action='store_true', help="Use a more agressive control file to achieve better convergence")
    msm_info.add_argument("--lagtime", type=int,  help="MSM Lagtime", default=100)
    msm_info.add_argument("--msm_clust", type=int,  help="MSM cluster number", default=200)


    #in_out simulation
    dissociation_info = parser.add_argument_group('\nDissociation path Simulation') 
    dissociation_info.add_argument("--in_out", action="store_true",  help="Launch dissotiation path adaptive")
    dissociation_info.add_argument("--in_out_soft", action="store_true",  help="Launch soft dissotiation path adaptive")


    #Exit simulation
    exit_info = parser.add_argument_group('\nExit Simulation') 
    exit_info.add_argument("--exit", action="store_true",  help="Exit simulation given certain condition")
    exit_info.add_argument("--exit_value", type=float,  help="Value of the metric used to exit simulation", default=0.95)
    exit_info.add_argument("--exit_condition", type=str,  help="Selects wether to exit the simulation when being over o below the exit value", default=">")
    exit_info.add_argument("--exit_trajnum", type=str,  help="Number of trajectories to accomplished the condition to exit the simulation", default=4)

    #Water simulation
    water_info = parser.add_argument_group('\nWater Simulation') 
    water_info.add_argument("--water_exp", type=str,  help="Launch water exploration adaptive PELE", default=None)
    water_info.add_argument("--water_lig", nargs="+",  help="Launch ligand-water exploration adaptive PELE", default=None)
    water_info.add_argument("--water_center", nargs="+",  help="Launch ligand-water exploration adaptive PELE", default=None)
    water_info.add_argument("--water_temp",  type=int, help="Temperature of water MC. i.e --water_temp 1000 default=500", default=500)
    water_info.add_argument("--water_constr",  type=float, help="Constraint on the waters MC. i.e ----water_const 0.5 default=0.2", default=0.2)
    water_info.add_argument("--water_trials",  type=int, help="Steric trials on the waters MC. i.e --water_trials 2000 default=1000", default=1000)


    #Bias simulation
    bias_info = parser.add_argument_group('\nBias Simulation') 
    bias_info.add_argument("--bias", action="store_true",  help="Launch biased simulation")

    
    #Induced fit simulation
    induced_fit_info = parser.add_argument_group('\nInduced fit simulation') 
    induced_fit_info.add_argument("--induce_fit", action="store_true",  help="Launch induce fit adaptive")



    args = parser.parse_args(args) if args else parser.parse_args()

    return args

def set_software_to_use(arguments):
    """
    Auxiliar Function to set low variable software
    which will be use to handle differences 
    between PELE features along the program
    """
    if arguments.hbond[0]:
        setattr(arguments, "software", "glide")
    elif arguments.water_lig or arguments.full or arguments.water_exp or arguments.in_out_soft or arguments.in_out or arguments.induce_fit or  (arguments.adaptive and arguments.pele) or arguments.bias:
        setattr(arguments, "software", "adaptive")
    elif arguments.msm:
        setattr(arguments, "software", "msm")
    elif arguments.frag and arguments.ca and arguments.fa:
        setattr(arguments, "software", "frag")
    else:
        #Standard Option
        setattr(arguments, "software", "adaptive")


def main(arguments):
    """
    Main function that sets the functionality
    of the software that will be used [Pele, Adaptive, glide...]
    and launch the respective job
    """
    set_software_to_use(arguments)
    job = Launcher(arguments)
    job.launch()
    return job


if __name__ == "__main__":
    arguments = parseargs()
    job = main(arguments)
