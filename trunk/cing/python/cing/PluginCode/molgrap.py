"""
Adds methods:
    Molecule.export2gif()
"""
from cing import cingDirMolmolScripts
from cing import cingDirTmp
from cing import cingRoot
from cing.Libs.NTutils import ExecuteProgram
from cing.Libs.NTutils import NTdebug
from cing.Libs.NTutils import NTdict
from cing.Libs.NTutils import NTerror
from cing.Libs.NTutils import NTpath
from cing.Libs.NTutils import NTwarning
from cing.Libs.TypeChecking import check_string
from cing.Libs.TypeChecking import check_type
from cing.core.constants import CYANA
from cing.core.molecule import Molecule
from cing.core.parameters import cingPaths
from cing.core.parameters import directories
import os

class Molgrap(NTdict):
    def __init__(self, backcolor='cing_turqoise', project=None):
        self.csh_script_dir = cingDirMolmolScripts
        self.backcolor = backcolor # see csh script definitions.
#        self.backcolor = 'bmrb_yellow' # see csh script definitions.
#        self.backcolor = 'cing_turqoise' # see csh script definitions.
#        self.backcolor = 'white' # see csh script definitions.
        self.projectDirTmp = cingDirTmp
        if project:
            self.projectDirTmp = os.path.abspath( project.path( directories.tmp ) )
        NTdebug('Using self.projectDirTmp: ' + self.projectDirTmp)

    """Creates a large gif to path for the given molecule.
    Return True on error and False on success.
    """
    def run(self, molecule, path, export = True):

        if not os.environ.has_key('MOLMOLHOME'):
            NTdebug('MOLMOLHOME not defined by user, using a temporary one')
            os.putenv('MOLMOLHOME', self.projectDirTmp)

        apath = os.path.abspath(path)
        if apath != path:
#            NTdebug("Using the absolute path ["+apath+"] from relative path: [" +path+"]")
            path = apath
        root,file,_ext  = NTpath(path)
        entry_code = file


        if root and not os.path.exists(root):
            NTerror("Molgrap.run: Given path root is absent; not creating.")
            return True

        pdb_first_file_name = os.path.join(self.projectDirTmp, file + "_001.pdb")
        pov_file_name       = os.path.join(self.projectDirTmp, file + ".pov")
        pov_cor_file_name   = os.path.join(self.projectDirTmp, file + "_cor.pov")

#        NTdebug( "pdb_first_file_name: "+ pdb_first_file_name)

        if not os.path.exists(pdb_first_file_name):
            export = True

        if export:
            NTdebug("First looking for atoms that should not be fed to molmol")
            NTdebug("Just as a side note once a Calcium in an xeasy project example screwed up the image generation.")
            skippedAtoms = [] # Keep a list of skipped atoms for later
            skippedResidues = []
            for res in molecule.allResidues():
#                TODO: why do the ions from the example xeasy project need to be removed here?
#                they cause molmol to write an invalid povray file.
#                consider switching to PyMol.
                if not (res.hasProperties('protein') or res.hasProperties('nucleic')):
                    skippedResidues.append(res)
                    for atm in res.allAtoms():
                        atm.pdbSkipRecord = True
                        skippedAtoms.append( atm )
            if skippedResidues:
                NTwarning('Molgrap.run: non-protein residues will be skipped:' + `skippedResidues`)
            # Molmol speaks Dyana which is close to cyana but residue names need to be translated to
            #
            molecule.toPDBfile(pdb_first_file_name, convention=CYANA, model=0)
            # Restore the 'default' state
            for atm in skippedAtoms:
                atm.pdbSkipRecord = False

        if not os.path.exists(pdb_first_file_name):
            NTerror("Molgrap.run: Failed to materialize first model PDB file")
            return True

#        NTdebug("Doing molmol on: "+ entry_code)

        status = self._make_molmol_pov_file(
            pdb_first_file_name,
            entry_code,
            self.backcolor
        )

        if status:
            NTerror( "Molgrap.run: while doing molmol for: "+ entry_code)
            return True

        if not os.path.isfile( pov_file_name ):
            NTerror('Molgrap.run: failed to generate povray file "%s" for %s', pov_file_name, entry_code)
            return True

        status = self._substitute_nans(
                pov_file_name,
                pov_cor_file_name
            )
        if status:
            NTerror("Molgrap.run: Doing molmol_povray_substitute._substitute_nans for: "+ entry_code)
            return True

        if not os.path.isfile( pov_cor_file_name ):
            NTerror("Molgrap.run: no corrected pov ray file generated for: " + entry_code)
            return True

#        print "DEBUG: Doing render/convert", entry_code

        status = self._render_convert_pov_file(
            pov_file_name   =pov_cor_file_name,
            id              =entry_code,
            results_dir     =root,
            )
        if status:
            print "Molgrap.run: rendering/converting entry:", entry_code
            return True

#        ## Remove temporary files if successful and possible
#        try:
#            os.unlink( pdb_first_file_name )
#            os.unlink( pov_file_name )
#            os.unlink( pov_cor_file_name )
#        except:
#            pass


    """
    Makes molmol images using a csh script. Note that these commands are only valid
    on Unix.
    """
    def _make_molmol_pov_file(self, pdb_file_name, id, backcolor  ):
        script_file_name = os.path.join ( self.projectDirTmp, id + "_molmol.csh" )
        log_file_name    = os.path.join ( self.projectDirTmp, id + "_molmol_python.log" )
        script_file = open(script_file_name, 'w')
        script_file.write('#!/bin/csh\n')
        script_file.write('set id              = %s\n' % id)
        script_file.write('set csh_script_dir  = %s\n' % self.csh_script_dir)
        script_file.write('set tmp_dir         = %s\n' % self.projectDirTmp)
        script_file.write('set pdb_file        = %s\n' % pdb_file_name)
        script_file.write('set backcolor       = %s\n' % backcolor)
        script_file.write('set executableMm    = %s\n' % cingPaths.molmol )
        script_file.write('set mac_dir         = %s\n' % os.path.join( cingRoot, "scripts", "molmol" ))
        script_file.write('\n')
        script_file.write('$csh_script_dir/molmol_image.csh $pdb_file $tmp_dir $id $csh_script_dir $backcolor $executableMm $mac_dir \n')
        script_file.write('exit $status\n')
        script_file.close()
        os.chmod(script_file_name,0755)
        program = ExecuteProgram(script_file_name, rootPath = self.projectDirTmp,redirectOutputToFile = log_file_name)
        if program(""):
            NTerror( "Failed shell command: " + script_file_name)
            return True
#        try:
#            os.unlink(script_file_name)
#            os.unlink(log_file_name)
#        except:
#            pass
        return None # not needed
    """
    Render pov ray file and convert output using a csh script.
    """
    def _render_convert_pov_file(self, pov_file_name, id, results_dir ):

        script_file_name = os.path.join ( self.projectDirTmp, id + "_render_convert_pov.csh" )
        log_file_name    = os.path.join ( self.projectDirTmp, id + "_render_convert_pov_python.log" )
        script_file = open(script_file_name, 'w')
        script_file.write('#!/bin/csh\n')
        script_file.write('set id              = %s\n' % id)
        script_file.write('set csh_script_dir  = %s\n' % self.csh_script_dir)
        script_file.write('set results_dir     = %s\n' % results_dir )
        script_file.write('set tmp_dir         = %s\n' % self.projectDirTmp)
        script_file.write('set pov_file_name   = %s\n' % pov_file_name)
        script_file.write('set executablePov   = %s\n' % cingPaths.povray )
        script_file.write('set executableConv  = %s\n' % cingPaths.convert )
        script_file.write('\n')
        script_file.write('$csh_script_dir/render_convert.csh $pov_file_name $tmp_dir $id $results_dir $executablePov $executableConv \n')
        script_file.write('exit $status\n')
        script_file.close()
        os.chmod(script_file_name,0755)


        program = ExecuteProgram(script_file_name, rootPath = self.projectDirTmp,redirectOutputToFile = log_file_name)
        if program(""):
            NTerror( "Failed shell command: " + script_file_name)
            NTerror("Have you installed povray-includes or similar?\n      For some Linuxes 'colors.inc' doesn't come with povray")
            return True
#        try:
#            os.unlink(script_file_name)
#            os.unlink(log_file_name)
#        except:
#            pass
        return None # not needed

    """
    Setup replacement lists
    Can not use a dictionary as order of replacements matter.
    """
    def _substitute_nans(self, file_name_in, file_name_out ):
        org = [
            r'<nan, nan, nan>, <nan, nan, nan>, <nan, nan, nan>',
            r'<nan, nan, nan>',
            r'<nan, nan,',
            ]
        new = [
            r'<0.0, 0.0, 0.0>, <0.1, 0.0, 0.0>, <0.0, 0.1, 0.0>',
            r'<0.0, 0.0, 0.0>',
            r'<0.0, 0.0,',
            ]
        self._substitute( file_name_in, file_name_out, org, new )

    """
    Substitute from a dictionary the content of a file writting to another
    """
    def _substitute(self, file_name_in, file_name_out, org, new ):

        output_text = open( file_name_in, 'r' ).read()
        for i in range( len(org) ):
            #print "DEBUG: Doing replace of: org[i]"
            output_text = output_text.replace( org[i], new[i])
        open( file_name_out, 'w' ).write( output_text )

def export2gif(molecule, path, project=None ):
    check_type(molecule,'Molecule')
    check_string(path)
    if project:
        check_type(project, 'Project')
#    NTdebug("Now in cing.Plugincode.molgrap#export2gif")
    m = Molgrap(project=project)
    m.run(molecule, path)

Molecule.export2gif = export2gif

# register the functions
methods  = []