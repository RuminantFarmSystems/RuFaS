.. _animal-output-files :

=======================
**Animal Output files**
=======================

U – user/ default; N – nutrition; M – management E – economics; W –
water; EN – energy in red: temporary, need update

Animal life cycle module:

   1. Imports:

      a. Herd:

       (1) Breed type (M)

       (2) Herd size (M)

       (3) Cow number (M)

       (4) Simulating days (M)

       (5) Grouping strategy (M)

      b. Animal:

+--------------------------------+-------------------------------------+
| (1) Animal ID (U)              | Initialize with simulation          |
+================================+=====================================+
| (2) Birth season (U)           | Birth season (U)                    |
+--------------------------------+-------------------------------------+
| (3) Birthday (U)               | Birth weight (U)                    |
+--------------------------------+-------------------------------------+
| (4) Body weight (N)            | Average daily gain (U)              |
+--------------------------------+-------------------------------------+


      c. Breeding:

       (1) Repro method: (U)

         Estrus detection
         Timed AI
         ED-TAI
         Synch protocol:
         Injection plan
         Hormonal choice
         Estrus detection rate
         Conception rate
         Voluntary waiting period

      d. Lactation: (U)

       (1) Curve

       (2) Record

       (3) Production level

      e. Body weight pattern (N, U)

       (1) Calf

       (2) Heifer

       (3) Pregnant heifer

       (4) 1\ :sup:`st`\ lactating cow

       (5) Later lactation cow

       (6) Dry cow

      f. Health: (U)

       (1) Calf health

       (2) Heifer health

       (3) Cow health

      g. Culling: (M)

       (1) Involuntary culling

       (2) Voluntary culling

      h. Market price: (E)

       (1) Heifer

       (2) Milk

       (3) Beef

       (4) Feed

       (5) Hormone

   2. Exports:

      a. Herd structure: (N, W, EN)

       (1) Newborn

       (2) Calves

       (3) Pre-breeding heifers

       (4) Post-breeding heifers

       (5) Replacement

       (6) Lactating cows (each lactation)

       (7) Culled animals (E)

      b. Breeding stats: (U, E)

       (1) AI number

       (2) Pregnancy rate

       (3) Injection cost

      c. Production: (N, E)

       (1) Daily milk production

       (2) Daily milk components

      d. Feed and water consumption (E, W, M)

       (weight*0.03)

      e. Manure production (M)

       (weight*0.06)

   3. System storage:

      a. Events of each animal:

       (1) Birth

       (2) Breeding:

         Estrus
         Injection
         Insemination
         Pregnancy checks
         Abortion
         Calving/ stillbirth
         Cull

       (3) Status:

         Lactation number
         Pregnancy days
         Days in milk
         Body weight
