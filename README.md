ECA - Event Condition Action
=================================

ECA was developed as an educational tool aimed at a diverse CS student 
population with programming experience ranging from "very little" to "very 
much": it allows students to quickly develop a prototype real-time Twitter 
Dashboard that really looks cool. And it is open to more advanced programming 
to challenge students who have more experience.
The basis of ECA is a rule system that reacts to externally generated events.

The architecture favours simplicity over robustness. Multithreading is used in
favour of more suitable parallelism options such as greenlets to keep
dependencies to a minimum for ease of deployment.

Documentation can be found in the Wiki of this github site.

This program is not intended for production use. It may contain security issues
not tolerable outside of a controlled environment.

ECA requires Python 3.2 or higher.




