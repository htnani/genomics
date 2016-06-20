#     mock.py: module providing mock Illumina data for testing
#     Copyright (C) University of Manchester 2012-2016 Peter Briggs
#
########################################################################

"""
mock.py

Provides classes for mocking up examples of outputs from Illumina-based
sequencers pipeline (e.g. GA2x or HiSeq), including example directory
structures, to be used in testing.

These include:

- MockIlluminaRun
- MockIlluminaData

"""

#######################################################################
# Import modules that this module depends on
#######################################################################

import os
import shutil
import bcftbx.utils
from bcftbx.IlluminaData import IlluminaFastq

#######################################################################
# Class definitions
#######################################################################

class MockIlluminaRun:
    """
    Utility class for creating mock Illumina sequencer output dirctories

    Example usage:

    >>> mockrun = MockIlluminaRun('151125_AB12345_001_CD256X','miseq')
    >>> mockrun.create()

    To delete the physical directory structure when finished:

    >>> mockrun.remove()

    """
    def __init__(self,name,platform,top_dir=None):
        """
        Create a new MockIlluminaRun instance

        Arguments:
          name (str): name for the run (used as top-level dir)
          platform (str): sequencing platform e.g. 'miseq', 'hiseq'
            'nextseq'
          top_dir (str): optionally specify a parent directory for
            the mock run (default is the current working directory)

        """
        self._created = False
        self._name = name
        if top_dir is not None:
            self._top_dir = os.path.abspath(top_dir)
        else:
            self._top_dir = os.getcwd()
        if platform not in ('miseq','hiseq','nextseq'):
            raise Exception("Unrecognised platform: %s" % platform)
        self._platform = platform

    @property
    def name(self):
        """
        Name of the mock run

        """
        return self._name

    @property
    def dirn(self):
        """
        Full path to the mock run directory

        """
        return os.path.join(self._top_dir,self._name)

    def _path(self,*dirs):
        """
        Return path under run directory

        """
        dirs0 = [self.dirn]
        dirs0.extend(dirs)
        return os.path.join(*dirs0)

    def _create_miseq(self):
        """Internal: creates mock MISeq run directory structure

        """
        # Constants for MISeq
        nlanes = 1
        ntiles = 12 #158
        ncycles = 218
        bcl_ext = '.bcl'
        # Basic directory structure
        bcftbx.utils.mkdir(self._path('Data'))
        bcftbx.utils.mkdir(self._path('Data','Intensities'))
        bcftbx.utils.mkdir(self._path('Data','Intensities','BaseCalls'))
        # Lanes
        for i in xrange(1,nlanes+1):
            # .locs files
            bcftbx.utils.mkdir(self._path('Data','Intensities','L%03d' % i))
            for j in xrange(1101,1101+ntiles):
                open(self._path('Data','Intensities','L%03d' % i,
                                's_%d_%d.locs' % (i,j)),'wb+').close()
            # BaseCalls
            bcftbx.utils.mkdir(self._path('Data','Intensities','BaseCalls',
                                          'L%03d' % i))
            for j in xrange(1101,1101+ntiles):
                open(self._path('Data','Intensities','BaseCalls',
                                'L%03d' % i,
                                's_%d_%d.control' % (i,j)),'wb+').close()
                open(self._path('Data','Intensities','BaseCalls',
                                'L%03d' % i,
                                's_%d_%d.filter' % (i,j)),'wb+').close()
            for k in xrange(1,ncycles+1):
                bcftbx.utils.mkdir(self._path('Data','Intensities','BaseCalls',
                                              'L%03d' % i,'C%d.1' % k))
                for j in xrange(1101,1101+ntiles):
                    open(self._path('Data','Intensities','BaseCalls',
                                    'L%03d' % i,'C%d.1' % k,
                                    's_%d_%d.%s' % (i,j,bcl_ext)),'wb+').close()
                    open(self._path('Data','Intensities','BaseCalls',
                                    'L%03d' % i,'C%d.1' % k,
                                    's_%d_%d.stats' % (i,j)),'wb+').close()
        # RunInfo.xml
        run_info_xml = """<?xml version="1.0"?>
<RunInfo xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" Version="2">
  <Run Id="%s" Number="1">
    <Flowcell>00000000-ABCD1</Flowcell>
    <Instrument>M00001</Instrument>
    <Date>150729</Date>
    <Reads>
      <Read Number="1" NumCycles="101" IsIndexedRead="N" />
      <Read Number="2" NumCycles="8" IsIndexedRead="Y" />
      <Read Number="3" NumCycles="8" IsIndexedRead="Y" />
      <Read Number="4" NumCycles="101" IsIndexedRead="N" />
    </Reads>
    <FlowcellLayout LaneCount="1" SurfaceCount="2" SwathCount="1" TileCount="19" />
  </Run>
</RunInfo>
"""
        with open(self._path('RunInfo.xml'),'w') as fp:
            fp.write(run_info_xml % self.name)
        # SampleSheet.csv
        sample_sheet_csv = """[Header],,,,,,,,,
IEMFileVersion,4,,,,,,,,
Date,11/23/2015,,,,,,,,
Workflow,GenerateFASTQ,,,,,,,,
Application,FASTQ Only,,,,,,,,
Assay,TruSeq HT,,,,,,,,
Description,,,,,,,,,
Chemistry,Amplicon,,,,,,,,
,,,,,,,,,
[Reads],,,,,,,,,
101,,,,,,,,,
101,,,,,,,,,
,,,,,,,,,
[Settings],,,,,,,,,
ReverseComplement,0,,,,,,,,
Adapter,AGATCGGAAGAGCACACGTCTGAACTCCAGTCA,,,,,,,,
AdapterRead2,AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGT,,,,,,,,
,,,,,,,,,
[Data],,,,,,,,,
Sample_ID,Sample_Name,Sample_Plate,Sample_Well,I7_Index_ID,index,I5_Index_ID,index2,Sample_Project,Description
Sample_1,Sample_1,,,D701,CGTGTAGG,D501,GACCTGTA,,
Sample_2,Sample_2,,,D702,CGTGTAGG,D501,ATGTAACT,,
"""
        with open(self._path('Data','Intensities','BaseCalls',
                             'SampleSheet.csv'),'w') as fp:
            fp.write(sample_sheet_csv)
        # (Empty) config.xml files
        open(self._path('Data','Intensities','config.xml'),'wb+').close()
        open(self._path('Data','Intensities','BaseCalls','config.xml'),
             'wb+').close()

    def _create_hiseq(self):
        """
        Internal: creates mock HISeq run directory structure

        """
        # Constants for HISeq
        nlanes = 8
        ntiles = 12 #1216
        ncycles = 218
        bcl_ext = '.bcl.gz'
        # Basic directory structure
        bcftbx.utils.mkdir(self._path('Data'))
        bcftbx.utils.mkdir(self._path('Data','Intensities'))
        bcftbx.utils.mkdir(self._path('Data','Intensities','BaseCalls'))
        # Lanes
        for i in xrange(1,nlanes+1):
            # .clocs files
            bcftbx.utils.mkdir(self._path('Data','Intensities','L%03d' % i))
            for j in xrange(1101,1101+ntiles):
                open(self._path('Data','Intensities','L%03d' % i,
                                's_%d_%d.clocs' % (i,j)),'wb+').close()
            # BaseCalls
            bcftbx.utils.mkdir(self._path('Data','Intensities','BaseCalls',
                                          'L%03d' % i))
            for j in xrange(1101,1101+ntiles):
                open(self._path('Data','Intensities','BaseCalls',
                                'L%03d' % i,
                                's_%d_%d.control' % (i,j)),'wb+').close()
                open(self._path('Data','Intensities','BaseCalls',
                                'L%03d' % i,
                                's_%d_%d.filter' % (i,j)),'wb+').close()
            for k in xrange(1,ncycles+1):
                bcftbx.utils.mkdir(self._path('Data','Intensities','BaseCalls',
                                              'L%03d' % i,'C%d.1' % k))
                for j in xrange(1101,1101+ntiles):
                    open(self._path('Data','Intensities','BaseCalls',
                                    'L%03d' % i,'C%d.1' % k,
                                    's_%d_%d.%s' % (i,j,bcl_ext)),'wb+').close()
                    open(self._path('Data','Intensities','BaseCalls',
                                    'L%03d' % i,'C%d.1' % k,
                                    's_%d_%d.stats' % (i,j)),'wb+').close()
        # RunInfo.xml
        run_info_xml = """<?xml version="1.0"?>
<RunInfo xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" Version="2">
  <Run Id="%s" Number="2">
    <Flowcell>A00NAABXX</Flowcell>
    <Instrument>H00002</Instrument>
    <Date>151113</Date>
    <Reads>
      <Read Number="1" NumCycles="101" IsIndexedRead="N" />
      <Read Number="2" NumCycles="8" IsIndexedRead="Y" />
      <Read Number="3" NumCycles="8" IsIndexedRead="Y" />
      <Read Number="4" NumCycles="101" IsIndexedRead="N" />
    </Reads>
    <FlowcellLayout LaneCount="8" SurfaceCount="2" SwathCount="3" TileCount="16" />
    <AlignToPhiX>
      <Lane>1</Lane>
      <Lane>2</Lane>
      <Lane>3</Lane>
      <Lane>4</Lane>
      <Lane>5</Lane>
      <Lane>6</Lane>
      <Lane>7</Lane>
      <Lane>8</Lane>
    </AlignToPhiX>
  </Run>
</RunInfo>
"""
        with open(self._path('RunInfo.xml'),'w') as fp:
            fp.write(run_info_xml % self.name)
        # SampleSheet.csv
        sample_sheet_csv = """[Header],,,,,,,,,,
IEMFileVersion,4,,,,,,,,,
Date,11/11/2015,,,,,,,,,
Workflow,GenerateFASTQ,,,,,,,,,
Application,HiSeq FASTQ Only,,,,,,,,,
Assay,Nextera XT,,,,,,,,,
Description,,,,,,,,,,
Chemistry,Amplicon,,,,,,,,,
,,,,,,,,,,
[Reads],,,,,,,,,,
101,,,,,,,,,,
101,,,,,,,,,,
,,,,,,,,,,
[Settings],,,,,,,,,,
ReverseComplement,0,,,,,,,,,
Adapter,CTGTCTCTTATACACATCT,,,,,,,,,
,,,,,,,,,,
[Data],,,,,,,,,,
Lane,Sample_ID,Sample_Name,Sample_Plate,Sample_Well,I7_Index_ID,index,I5_Index_ID,index2,Sample_Project,Description
1,AB1,AB1,,,N701,TAAGGCGA,S504,AGAGTAGA,AB,
2,TM2,TM1,,,N701,TAAGGCGA,S517,GCGTAAGA,TM,
3,CD3,CD3,,,N701,GTGAAACG,S503,TCTTTCCC,CD,
4,EB4,EB4,,A1,N701,TAAGGCGA,S501,TAGATCGC,EB,
5,EB5,EB5,,A3,N703,AGGCAGAA,S501,TAGATCGC,EB,
6,EB6,EB6,,F3,N703,AGGCAGAA,S506,ACTGCATA,EB,
7,ML7,ML7,,,N701,GCCAATAT,S502,TCTTTCCC,ML,
8,VL8,VL8,,,N701,GCCAATAT,S503,TCTTTCCC,VL,
"""
        with open(self._path('Data','Intensities','BaseCalls',
                             'SampleSheet.csv'),'w') as fp:
            fp.write(sample_sheet_csv)
        # (Empty) config.xml files
        open(self._path('Data','Intensities','config.xml'),'wb+').close()
        open(self._path('Data','Intensities','BaseCalls','config.xml'),
             'wb+').close()

    def _create_nextseq(self):
        """
        Internal: creates mock NextSeq run directory structure

        """
        # Constants for NextSeq
        nlanes = 4
        ntiles = 158
        bcl_ext = '.bcl.bgzf'
        # Basic directory structure
        bcftbx.utils.mkdir(self._path('Data'))
        bcftbx.utils.mkdir(self._path('Data','Intensities'))
        bcftbx.utils.mkdir(self._path('Data','Intensities','BaseCalls'))
        bcftbx.utils.mkdir(self._path('InterOp'))
        # Lanes
        for i in xrange(1,nlanes+1):
            # .locs files
            bcftbx.utils.mkdir(self._path('Data','Intensities','L%03d' % i))
            open(self._path('Data','Intensities','L%03d' % i,'s_%d.locs' % i),
                 'wb+').close()
            # BaseCalls
            bcftbx.utils.mkdir(self._path('Data','Intensities','BaseCalls',
                                          'L%03d' % i))
            open(self._path('Data','Intensities','BaseCalls','L%03d' % i,
                            's_%d.bci' % i),'wb+').close()
            open(self._path('Data','Intensities','BaseCalls','L%03d' % i,
                            's_%d.filter' % i),'wb+').close()
            for j in xrange(1,ntiles+1):
                open(self._path('Data','Intensities','BaseCalls','L%03d' % i,
                                '%04d%s' % (j,bcl_ext)),'wb+').close()
                open(self._path('Data','Intensities','BaseCalls','L%03d' % i,
                                '%04d%s.bci' % (j,bcl_ext)),'wb+').close()
        # RunInfo.xml
        run_info_xml = """<?xml version="1.0"?>
<RunInfo xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.o
rg/2001/XMLSchema-instance" Version="4">
  <Run Id="%s" Number="1">
    <Flowcell>ABC1234XX</Flowcell>
    <Instrument>N000003</Instrument>
    <Date>151123</Date>
    <Reads>
      <Read Number="1" NumCycles="76" IsIndexedRead="N" />
      <Read Number="2" NumCycles="6" IsIndexedRead="Y" />
      <Read Number="3" NumCycles="76" IsIndexedRead="N" />
    </Reads>
    <FlowcellLayout LaneCount="4" SurfaceCount="2" SwathCount="3" TileCount="12"
 SectionPerLane="3" LanePerSection="2">
      <TileSet TileNamingConvention="FiveDigit">
        <Tiles>
          <Tile>1_11101</Tile>
          <Tile>1_21101</Tile></Tiles>
      </TileSet>
    </FlowcellLayout>
    <ImageDimensions Width="2592" Height="1944" />
    <ImageChannels>
      <Name>Red</Name>
      <Name>Green</Name>
    </ImageChannels>
  </Run>
</RunInfo>"""
        with open(self._path('RunInfo.xml'),'w') as fp:
            fp.write(run_info_xml % self.name)

    def create(self):
        """
        Build and populate the directory structure

        Creates the directory structure on disk which has been defined
        within the MockIlluminaRun object.

        Invoke the 'remove' method to delete the directory structure.

        'create' raises an OSError exception if any part of the directory
        structure already exists.

        """
        # Create top level directory
        if os.path.exists(self.dirn):
            raise OSError,"%s already exists" % self.dirn
        else:
            bcftbx.utils.mkdir(self.dirn)
            self._created = True
        # Make platform-specific directory structure
        if self._platform == 'miseq':
            self._create_miseq()
        elif self._platform == 'hiseq':
            self._create_hiseq()
        elif self._platform == 'nextseq':
            self._create_nextseq()

    def remove(self):
        """
        Delete the directory structure and contents

        This removes the directory structure from disk that has
        previously been created using the create method.

        """
        if self._created:
            shutil.rmtree(self.dirn)
            self._created = False

class MockIlluminaData:
    """Utility class for creating mock Illumina analysis data directories

    The MockIlluminaData class allows artificial Illumina analysis data
    directories to be defined, created and populated, and then destroyed.

    These artifical directories are intended to be used for testing
    purposes.

    Two styles of analysis directories can be produced: 'casava'-style
    aims to mimic that produced from the CASAVA and bcl2fastq 1.8
    processing software; 'bcl2fastq2' mimics that from the bcl2fastq
    2.* software.

    Basic example usage:

    >>> mockdata = MockIlluminaData('130904_PJB_XXXXX','casava')
    >>> mockdata.add_fastq('PJB','PJB1','PJB1_GCCAAT_L001_R1_001.fastq.gz')
    >>> ...
    >>> mockdata.create()

    This will make a CASAVA-style directory structure like:

    1130904_PJB_XXXXX/
        Unaligned/
            Project_PJB/
                Sample_PJB1/
                    PJB1_GCCAAT_L001_R1_001.fastq.gz
        ...

    Using:

    >>> mockdata = MockIlluminaData('130904_PJB_XXXXX','bcl2fastq2')
    >>> mockdata.add_fastq('PJB','PJB1','PJB1_S1_L001_R1_001.fastq.gz')

    will make a bcl2fast2-style directory structure like:

    1130904_PJB_XXXXX/
        Unaligned/
            PJB/
               PJB1_S1_L001_R1_001.fastq.gz
        ...

    NB if the sample name in the fastq file name differs from the supplied
    sample name then the sample name will be used to create an additional
    directory level, e.g.:

    >>> mockdata = MockIlluminaData('130904_PJB_XXXXX','bcl2fastq2')
    >>> mockdata.add_fastq('PJB','PJB2','PJB2_input_S1_L001_R1_001.fastq.gz')

    will create:

    1130904_PJB_XXXXX/
        Unaligned/
            PJB/
               PJB2/
                   PJB2_input_S1_L001_R1_001.fastq.gz
        ...

    (this replicates the situation for bcl2fastq v2 where Sample_ID and
    Sample_Name differ.)

    Multiple fastqs can be more easily added using e.g.:

    >>> mockdata.add_fastq_batch('PJB','PJB2','PJB1_GCCAAT',lanes=(1,4,5))

    which creates 3 fastq entries for sample PJB2, with lane numbers 1, 4
    and 5.

    Paired-end mock data can be created using the 'paired_end' flag
    when instantiating the MockIlluminaData object.

    To delete the physical directory structure when finished:

    >>> mockdata.remove()

    """
    def __init__(self,name,package,
                 unaligned_dir='Unaligned',
                 paired_end=False,
                 no_lane_splitting=False,
                 top_dir=None):
        """Create new MockIlluminaData instance

        Makes a new empty MockIlluminaData object.

        Arguments:
          name: name of the directory for the mock data
          package: name of the conversion software package to mimic (can
            be 'casava' or 'bcl2fastq2')
          unaligned_dir: directory holding the mock projects etc (default is
            'Unaligned')
          paired_end: specify whether mock data is paired end (True) or not
            (False) (default is False)
          no_lane_splitting: (bcl2fastq2 only) mimick output from bcl2fastq2
            run with --no-lane-splitting (i.e. fastq names don't contain
            lane numbers) (default is False)
          top_dir: specify a parent directory for the mock data (default is
            the current working directory)

        """
        self.__created = False
        self.__name = name
        if package not in ('casava','bcl2fastq2'):
            raise Exception("Unknown package '%s': cannot make mock output dir"
                            % package)
        self.__package = package
        self.__unaligned_dir = unaligned_dir
        self.__paired_end = paired_end
        if package == 'bcl2fastq2':
            self.__no_lane_splitting = no_lane_splitting
        else:
            self.__no_lane_splitting = False
        self.__undetermined_dir = 'Undetermined_indices'
        if top_dir is not None:
            self.__top_dir = os.path.abspath(top_dir)
        else:
            self.__top_dir = os.getcwd()
        self.__projects = {}

    @property
    def name(self):
        """Name of the mock data

        """
        return self.__name

    @property
    def package(self):
        """
        Software package output that is being mimicked

        """
        return self.__package

    @property
    def dirn(self):
        """Full path to the mock data directory

        """
        return os.path.join(self.__top_dir,self.__name)

    @property
    def unaligned_dir(self):
        """Full path to the unaligned directory for the mock data

        """
        return os.path.join(self.dirn,self.__unaligned_dir)

    @property
    def paired_end(self):
        """Whether or not the mock data is paired ended

        """
        return self.__paired_end

    @property
    def projects(self):
        """List of project names within the mock data

        """
        projects = []
        for project_name in self.__projects:
            if project_name.startswith('Project_'):
                projects.append(project_name.split('_')[1])
            else:
                projects.append(project_name)
        projects.sort()
        return projects

    @property
    def has_undetermined(self):
        """Whether or not undetermined indices are included

        """
        return (self.__undetermined_dir in self.__projects)

    def samples_in_project(self,project_name):
        """List of sample names associated with a specific project

        Arguments:
          project_name: name of a project

        Returns:
          List of sample names

        """
        project = self.__projects[self.__project_dir(project_name)]
        samples = []
        for sample_name in project:
            if sample_name.startswith('Sample_'):
                samples.append(sample_name.split('_')[1])
            else:
                samples.append(sample_name)
        samples.sort()
        return samples

    def fastqs_in_sample(self,project_name,sample_name):
        """List of fastq names associated with a project/sample pair

        Arguments:
          project_name: name of a project
          sample_name: name of a sample

        Returns:
          List of fastq names.

        """
        project_dir = self.__project_dir(project_name)
        sample_dir = self.__sample_dir(sample_name)
        return self.__projects[project_dir][sample_dir]

    def __project_dir(self,project_name):
        """Internal: convert project name to internal representation

        Project names which are prepended with "Project_" will have this
        part removed.

        Arguments:
          project_name: name of a project

        Returns:
          Canonical project name for internal storage.

        """
        if project_name.startswith('Project_'):
            return project_name[8:]
        else:
            return project_name

    def __sample_dir(self,sample_name):
        """Internal: convert sample name to internal representation

        Sample names which are prepended with "Sample_" will have this
        part removed.

        Arguments:
          sample_name: name of a sample

        Returns:
          Canonical sample name for internal storage.

        """
        if sample_name.startswith('Sample_'):
            return sample_name[7:]
        else:
            return sample_name

    def add_project(self,project_name):
        """Add a project to the MockIlluminaData instance

        Defines a project within the MockIlluminaData structure.
        Note that any leading 'Project_' is ignored i.e. the project
        name is taken to be the remainder of the name.

        No error is raised if the project already exists.

        Arguments:
          project_name: name of the new project

        Returns:
          Dictionary object corresponding to the project.

        """
        project_dir = self.__project_dir(project_name)
        if project_dir not in self.__projects:
            self.__projects[project_dir] = {}
        return self.__projects[project_dir]

    def add_sample(self,project_name,sample_name):
        """Add a sample to a project within the MockIlluminaData instance

        Defines a sample with a project in the MockIlluminaData
        structure. Note that any leading 'Sample_' is ignored i.e. the
        sample name is taken to be the remainder of the name.

        If the parent project doesn't exist yet then it will be
        added automatically; no error is raised if the sample already
        exists.

        Arguments:
          project_name: name of the parent project
          sample_name: name of the new sample

        Returns:
          List object corresponding to the sample.

        """
        project = self.add_project(project_name)
        sample_dir = self.__sample_dir(sample_name)
        if sample_dir not in project:
            project[sample_dir] = []
        return project[sample_dir]

    def add_fastq(self,project_name,sample_name,fastq):
        """Add a fastq to a sample within the MockIlluminaData instance

        Defines a fastq within a project/sample pair in the MockIlluminaData
        structure.

        NOTE: it is recommended to use add_fastq_batch, which offers more
        flexibility and automatically maintains consistency e.g. when
        mocking a paired end data structure.

        Arguments:
          project_name: parent project
          sample_name: parent sample
          fastq: name of the fastq to add

        """
        sample = self.add_sample(project_name,sample_name)
        sample.append(fastq)
        sample.sort()

    def add_fastq_batch(self,project_name,sample_name,fastq_base,fastq_ext='fastq.gz',
                        lanes=(1,)):
        """Add a set of fastqs within a sample

        This method adds a set of fastqs within a sample with a single
        invocation, and is intended to simulate the situation where there
        are multiple fastqs due to paired end sequencing and/or sequencing
        of the sample across multiple lanes.

        The fastq names are constructed from a base name (e.g. 'PJB-1_GCCAAT'),
        plus a list/tuple of lane numbers. One fastq will be added for each
        lane number specified, e.g.:

        >>> d.add_fastq_batch('PJB','PJB-1','PJB-1_GCCAAT',lanes=(1,4,5))

        will add PJB-1_GCCAAT_L001_R1_001, PJB-1_GCCAAT_L004_R1_001 and
        PJB-1_GCCAAT_L005_R1_001 fastqs.

        If the MockIlluminaData object was created with the paired_end flag
        set to True then matching R2 fastqs will also be added.

        If the MockIlluminaData object was created with the no_lane_splitting
        flag set to True and the package as 'bcl2fastq' then the 'lanes'
        specification will be ignored and the fastq names will not contain
        lane identifiers.

        Arguments:
          project_name: parent project
          sample_name: parent sample
          fastq_base: base name of the fastq name i.e. just the sample name
            and barcode sequence (e.g. 'PJB-1_GCCAAT')
          fastq_ext: file extension to use (optional, defaults to 'fastq.gz')
          lanes: list, tuple or iterable with lane numbers (optional,
            defaults to (1,))

        """
        if self.__paired_end:
            reads = (1,2)
        else:
            reads = (1,)
        if not self.__no_lane_splitting:
            # Include explicit lane information
            for lane in lanes:
                for read in reads:
                    fastq = "%s_L%03d_R%d_001.%s" % (fastq_base,
                                                     lane,read,
                                                     fastq_ext)
                    self.add_fastq(project_name,sample_name,fastq)
        else:
            # Replicate output from bcl2fastq --no-lane-splitting
            for read in reads:
                fastq = "%s_R%d_001.%s" % (fastq_base,
                                           read,
                                           fastq_ext)
                self.add_fastq(project_name,sample_name,fastq)

    def add_undetermined(self,lanes=(1,)):
        """Add directories and files for undetermined reads

        This method adds a set of fastqs for any undetermined reads from
        demultiplexing.

        Arguments:
          lanes: list, tuple or iterable with lane numbers (optional,
            defaults to (1,))

        """
        if not self.__no_lane_splitting:
            for lane in lanes:
                sample_name = "lane%d" % lane
                if self.package == 'casava':
                    # CASAVA-style naming
                    fastq_base = "lane%d_Undetermined" % lane
                elif self.package == 'bcl2fastq2':
                    # bcl2fastq2-style naming
                    fastq_base = "Undetermined_S0"
                self.add_sample(self.__undetermined_dir,sample_name)
                self.add_fastq_batch(self.__undetermined_dir,sample_name,
                                     fastq_base,lanes=(lane,))
        else:
            sample_name = "undetermined"
            fastq_base = "Undetermined_S0"
            self.add_sample(self.__undetermined_dir,sample_name)
            self.add_fastq_batch(self.__undetermined_dir,sample_name,
                                 fastq_base,lanes=None)

    def create(self):
        """Build and populate the directory structure

        Creates the directory structure on disk which has been defined
        within the MockIlluminaData object.

        Invoke the 'remove' method to delete the directory structure.

        The contents of the MockIlluminaData object can be modified
        after the directory structure has been created, but changes will
        not be reflected on disk. Instead it is necessary to first
        remove the directory structure, and then re-invoke the create
        method.

        create raises an OSError exception if any part of the directory
        structure already exists.

        """
        # Create top level directory
        if os.path.exists(self.dirn):
            raise OSError,"%s already exists" % self.dirn
        else:
            bcftbx.utils.mkdir(self.dirn)
            self.__created = True
        # "Unaligned" directory
        bcftbx.utils.mkdir(self.unaligned_dir)
        if self.package == 'casava':
            self._populate_casava()
        elif self.package == 'bcl2fastq2':
            self._populate_bcl2fastq2()

    def _populate_casava(self):
        """
        Populate the MockIlluminaData structure in the style of CASAVA

        """
        # Populate with projects, samples etc
        for project_name in self.__projects:
            if project_name == self.__undetermined_dir:
                project_dirn = os.path.join(self.unaligned_dir,project_name)
            else:
                project_dirn = os.path.join(self.unaligned_dir,
                                            "Project_%s" % project_name)
            bcftbx.utils.mkdir(project_dirn)
            for sample_name in self.__projects[project_name]:
                sample_dirn = os.path.join(project_dirn,
                                           "Sample_%s" % sample_name)
                bcftbx.utils.mkdir(sample_dirn)
                for fastq in self.__projects[project_name][sample_name]:
                    fq = os.path.join(sample_dirn,fastq)
                    # "Touch" the file (i.e. creates an empty file)
                    open(fq,'wb+').close()

    def _populate_bcl2fastq2(self):
        """
        Populate the MockIlluminaData structure in the style of bcl2fastq2

        """
        for project_name in self.__projects:
            if project_name == self.__undetermined_dir:
                project_dirn = self.unaligned_dir
            else:
                project_dirn = os.path.join(self.unaligned_dir,project_name)
            bcftbx.utils.mkdir(project_dirn)
            for sample_name in self.__projects[project_name]:
                for fastq in self.__projects[project_name][sample_name]:
                    # Check if sample name matches that for fastq
                    fq_sample_name = IlluminaFastq(fastq).sample_name
                    if fq_sample_name != sample_name and \
                       fq_sample_name != 'Undetermined':
                        # Create an intermediate directory
                        sample_dirn = os.path.join(project_dirn,sample_name)
                        bcftbx.utils.mkdir(sample_dirn)
                    else:
                        sample_dirn = project_dirn
                    fq = os.path.join(sample_dirn,fastq)
                    # "Touch" the file (i.e. creates an empty file)
                    open(fq,'wb+').close()

    def remove(self):
        """Delete the directory structure and contents

        This removes the directory structure from disk that has
        previously been created using the create method.

        """
        if self.__created:
            shutil.rmtree(self.dirn)
            self.__created = False

    def __repr__(self):
        """Implement __repr__ for debug purposes
        """
        if not self.__created:
            return ("<%s: not created>" % self.dirn)
        rep = []
        for d in os.walk(self.dirn):
            for d1 in d[1]:
                rep.append(os.path.join(d[0],d1))
            for f in d[2]:
                rep.append(os.path.join(d[0],f))
        return '\n'.join(sorted(rep))
