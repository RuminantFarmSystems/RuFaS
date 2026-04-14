Model Review Process
====================

This document defines the process for reviewing the RuFaS model prior to a new version release. It complements the branching strategy, versioning policy, and maintainer workflow documentation.

The process consists of two phases:

- Pre-merge preparation
- Post-merge evaluation

Pre-Merge Preparation
---------------------

These steps may begin as soon as a new version release has been initiated and before merging development changes into the ``test`` branch.


Update Evaluation Farm Dataset
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- Ensure the evaluation farm input files are up to date and run without error on ``dev`` or on ``test`` after merging ``dev`` to ``test``.

Update Desired Outputs
^^^^^^^^^^^^^^^^^^^^^^

Update all outputs required for evaluation, including:

- RuFaS output filters
- Post-processing scripts
- Derived or summary outputs

Update Benchmarks
^^^^^^^^^^^^^^^^^

- Review and update benchmark datasets and expectations as needed.
- Ensure benchmarks reflect current model scope and scientific understanding.

Post-Merge Evaluation
---------------------

These steps occur after merging into the ``test`` branch.

Run Model Simulations
^^^^^^^^^^^^^^^^^^^^^

- Run evaluation farms using the updated model.
- Compile summarized results including comparison with previous results and benchmarks. 
- Responsibility: Scientific Director


Review Results Summary
^^^^^^^^^^^^^^^^^^^^^^

- Share results with Maintainer SMEs.
- At least one SME from each module must review before proceeding.

Iterate
^^^^^^^

- Repeat simulation and evaluation steps until results are acceptable.


Reporting and Review
--------------------

Prepare Report
^^^^^^^^^^^^^^

- Summarize:

  - Key results
  - Comparisons to benchmarks and prior versions
  - Notable changes

Review Report
^^^^^^^^^^^^^

- Similar to above, at least one SME from each module should review the report.
- Additional review from external or Contributor SMEs is recommended.

Approval Criteria
-----------------

Proceed toward release when:

- Each module is represented in both results review and report review.
- Model performance is acceptable relative to:

  - Benchmarks
  - Prior versions
  - Scientific expectations

Notes
-----

- This process is iterative and may be adapted as needed.
- Automation of datasets, outputs, and benchmarking workflows is encouraged to improve reproducibility and efficiency.