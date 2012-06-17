================
Autotest feature
================

Problems
========

Cocos has very few automatic tests
----------------------------------

Hence when modifying the cocos library we are at more risk to introduce bugs.


Hard to asses at release time if the scripts in test directory are behaving correctly or not
--------------------------------------------------------------------------------------------

At present they are 190+ scripts.
Many don't have a description to tell, by looking at the screen, if it is displaying as expected or not.
Hence it takes a lot of time to inspect them.  


Autotest, a partial solution
============================

The basic idea is:

Stage1: building the reference database

	+ have a script that runs all the tests, taking relevant screenshots
	+ human review for the snapshots determines if the test pass or fail
	
Stage2: asses (semi)automatically pass / fail for further cocos revisions

	+ run the script to take snapshots
	+ compare with images obtained in the reference run

		+ if equals, pass
		+ if too much different, fail 
		+ if difference under a threshold, human intervention is needed to decide.
		
The last point is needed because of small (or not so small) differences in render when using different openGL drivers.

The reference subsystem must report, at the least:

	+ which are the snapshots for script zzz?
	+ how was judged the script zzz results in the reference run ? (pass / fail, human assessed)
	+ was the script zzz changed between the reference run and this run ? Human inspection is required here.

While exploring different parts needed for this task a lot of detail that need to be handled emerged.
	
Status:

	+ clock subclasses that allow driving the scripts trough precise timestamps, done.
	+ clock variants for both pyglet 1.1.4release and 1.2dev, done.
	+ a variant to subprocess.Popen to run scripts with a timeout, done.
	+ specification, parsing and validation to describe what are the relevant states to snapshot, mostly done (needs upgrade to handle interactive scripts)
	+ a snapshot runner that will exercise a number of scripts, following the desired snapshot plan, collecting snapshots, tracebacks and other failures, done.
	+ define and write extractors for the info we need to store about each script, mostly done: scan, change detection, snapshots info, diagnostic covered; human generated info needs to be done
	+ information handling support (low level) adequate to the tasks, mostly done, probably will need some additional features
	+ A high level, small API to select meaningful subsets of scripts, perform tasks over them, do reports; partially done
	+ all scripts in test got initial refactor to cooperate with the snapshot_taker proxy
	+ add testinfo (the plan to take snapshots) to each test script: 95 / 193 done, snapshots taken
	
	
Working now (toward milestone 1+2)

	> adding testinfo to remaining test
	> expand testinfo spec and support for interactive tests using KBD, other interactions.
	> explore how to handle human assessment
		+ bulk register a bunch of test 'pass' (recon.py update_3)
	

Milestone 2
-----------

Capture complete reference info, including human pass-fail collection, for most test scripts (80% ?)


Milestone 3 (with this completed we have a usable tool)
-----------
	+ high level script to assist stating pass / fail (in the same SW / HW platform) with the help of the reference database
	+ handle and record fails due to hardware / software compatibility
	
Milestone 4 (eases access to this testing tool to new people)
-----------

	+ explore the variations across different testbeds to see if we need to recalibrate the reference when changing testbed ( say, ati 5670 to intel 945G)
	+ write / upgrade scripts to help recycle a reference database in other platforms 

Code
====
	+ recon.py : arena script to drive development of new high level functionality. Currently evolving to 'Capture a reference dataset, snapshot + other info'

	+ helpers.py : middle layer support. Implements the high level functionality with the aid of lower level functionality provided by remembercases. Most if not all would move to remembercases later.
	
	+ proxy_snapshots.py : proxy cocos specific, a middleman used by the capture snapshot script to run each target script

	+ test_helpers.py : unit tests. In debt here, postponed a bit while shuffling bits of code and trying API variations. I think most of current content of helpers.py is stable, so theres no excuse to not write some. 

