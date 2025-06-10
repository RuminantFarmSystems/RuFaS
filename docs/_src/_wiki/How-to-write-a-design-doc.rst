How To Write a Design Doc
=========================
This page is adopted from `this
article <https://www.freecodecamp.org/news/how-to-write-a-good-software-design-document-66fcf019569c/>`__
and is split into 4 sections:

- **Why** write a design document
- **What** to include in a design document
- **How** to write it
- The **process** around it

Why write a design document?
----------------------------

A design doc — also known as a technical spec — is a description of how
you plan to solve a problem.

There are `lots of
writings <https://www.joelonsoftware.com/2000/10/02/painless-functional-specifications-part-1-why-bother/>`__
already on why it’s important to write a design doc before diving into
coding. So all I’ll say here is:

**A design doc is the most useful tool for making sure the right work
gets done.**

The main goal of a design doc is to make you more effective by forcing
you to think through the design and gather feedback from others. People
often think the point of a design doc is to teach others about some
system or serve as documentation later on. While those can be beneficial
side effects, they are **not** the goal in and of themselves.

As a general rule of thumb, if you are working on a project that might
take 1 engineer-month or more, you should write a design doc. But don’t
stop there — a lot of smaller projects could benefit from a mini design
doc too.

What to include in a design doc?
--------------------------------

A design doc describes the solution to a problem. Since the nature of
each problem is different, naturally you’d want to structure your design
doc differently. A detailed template for the design doc can be found
`here <https://docs.google.com/document/d/10QExT4j9JXnc1MUUzOSG_vHKP7K2tTIplVxJ6OttDaQ/edit?usp=sharing>`__.
It includes:

- Title and people
- Overview
- Context
- Requirements
- Milestones
- Existing Solution
- Proposed Solution
- Alternative Solutions
- Testability, Monitoring, and Alerting
- Cross-Team Impact
- Open Questions
- Detailed Scoping and Timeline

How to write it
---------------

Write as simply as possible
---------------------------

Don’t try to write like the academic papers you’ve read. They are
written to impress journal reviewers. Your doc is written to describe
your solution and get feedback from your teammates. You can achieve
clarity by using:

- Simple words
- Short sentences
- Bulleted lists and/or numbered lists
- Concrete examples, like “User Alice connects her bank account, then …”

Add lots of charts and diagrams
-------------------------------

Charts can often be useful to compare several potential options, and
diagrams are generally easier to parse than text. *Google Drawing* and
*Draw.io* are two options to consider for drawing diagrams.

**Pro Tip:** remember to add a link to the editable version of the
diagram under the screenshot, so you can easily update it later when
things inevitably change.

Include numbers
---------------

The scale of the problem often determines the solution. To help
reviewers get a sense of the state of the world, include real numbers
like # of rows, # of animals, latency — and how these scale with usage.
Remember your Big-O notations?

Try to be funny
---------------

A spec is not an academic paper. Also, people like reading funny things,
so this is a good way to keep the reader engaged. Don’t overdo this to
the point of taking away from the core idea though.

Do the Skeptic Test
-------------------

Before sending your design doc to others to review, take a pass at it
pretending to be the reviewer. What questions and doubts might you have
about this design? Then address them preemptively.

Do the Vacation Test
--------------------

If you go on a long vacation now with no internet access, can someone on
your team read the doc and implement it as you intended? The main goal
of a design doc is not knowledge sharing, but this is a good way to
evaluate for clarity so that others can actually give you useful
feedback.

Process
-------

Design docs help you get feedback before you waste a bunch of time
implementing the wrong solution or the solution to the wrong problem.
There’s a lot of art to getting good feedback, but that’s for a later
article. For now, let’s just talk specifically about how to write the
design doc and get feedback for it.

First of all, everyone working on the project should be a part of the
design process. It’s okay if the tech lead ends up driving a lot of the
decisions, but everyone should be involved in the discussion and buy
into the design. So the “you” throughout this article is a really plural
“you” that includes all the people on the project.

Secondly, the design process doesn’t mean you staring at the whiteboard
theorizing ideas. Feel free to get your hands dirty and prototype
potential solutions. This is not the same as starting to write
production code for the project before writing a design doc. Don’t do
that. But you absolutely should feel free to write some hacky throwaway
code to validate an idea. To ensure that you only write exploratory
code, **make it a rule that none of this prototype code gets merged to
master.**

After that, as you start to have some idea of how to go about your
project, do the following:

1. Ask an experienced developer or SME on your team to be your reviewer.
   Ideally, this would be someone who’s well respected and/or familiar
   with the edge cases of the problem.
2. Go into a conference room with a whiteboard.
3. Describe the problem that you are tackling to this person(this is a
   very important step, don’t skip it!).
4. Then explain the implementation you have in mind, and convince them
   this is the right thing to build.

Doing all of this **before** you even start writing your design doc lets
you get feedback as soon as possible before you invest more time and get
attached to any specific solution. Often, even if the implementation
stays the same, your reviewer is able to point out corner cases you need
to cover, indicate any potential areas of confusion, and anticipate
difficulties you might encounter later on.

Then, after you’ve written a rough draft of your design doc, get the
same reviewer to read through it again, and rubber stamp it by adding
their name as the reviewer in the **Title and People** section of the
design doc. This creates additional incentives and accountability for
the reviewer.

Once you and the reviewer(s) sign off, feel free to send the design doc
to your team for additional feedback and knowledge sharing. I suggest
time-bounding this feedback-gathering process to about 1 week to avoid
extended delays. Commit to addressing all questions and comments people
leave within that week. **Leaving comments hanging = bad karma.**

Lastly, if there’s a lot of contention between you, your reviewer, and
other developers reading the doc, I strongly recommend consolidating all
the points of contention in the Discussion section of your doc. Then,
set up a meeting with the different parties to talk about these
disagreements in person.

Whenever a discussion thread is more than 5 comments long, moving to an
in-person discussion tends to be far more efficient. Keep in mind that
you are still responsible for making the final call, even if everyone
can’t come to a consensus.

Once you’ve done all the above, time to get going on the implementation!
For extra brownie points,*\* treat this design doc as a living document
as you implement the design.*\* Update the doc every time you learn
something that leads to you making changes to the original solution or
update your scoping. You’ll thank me later when you don’t have to
explain things over and over again to all your stakeholders.

How do we evaluate the success of a design doc?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*A design doc is successful if the right ROI of work is done.* That
means a successful design doc might actually lead to an outcome like
this:

1. You spend 5 days writing the design doc, this forces you to think
   through different parts of the technical architecture
2. You get feedback from reviewers that X is the riskiest part of the
   proposed architecture
3. You decide to implement X first to de-risk the project
4. 3 days later, you figure out that X is either not possible, or far
   more difficult than you originally intended
5. You decide to stop working on this project and prioritize other work
   instead

At the beginning of this article, we said **the goal of a design doc is
to make sure the right work gets done.** In the example above, thanks to
this design doc, instead of wasting potentially months only to abort
this project later, you’ve only spent 8 days. Seems like a pretty
successful outcome to me.
