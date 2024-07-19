# from owlready2 import *
import owlready2
owlready2.JAVA_EXE = r"C:\Program Files\Common Files\Oracle\Java\javapath\java.exe"
onto = owlready2.get_ontology("http://test.org/onto.owl")

print("classes: ", list(onto.classes()))
with onto:

    class Drug(owlready2.Thing):

        def take(self): print("I took a drug")

    class ActivePrinciple(owlready2.Thing):
        pass

    class has_for_active_principle(Drug >> ActivePrinciple):
        python_name = "active_principles"

    class Placebo(Drug):
        equivalent_to = [Drug & owlready2.Not(has_for_active_principle.some(ActivePrinciple))]
        def take(self): print("I took a placebo")

    class SingleActivePrincipleDrug(Drug):
        equivalent_to = [Drug & has_for_active_principle.exactly(1, ActivePrinciple)]
        def take(self): print("I took a drug with a single active principle")

    class DrugAssociation(Drug):
        equivalent_to = [Drug & has_for_active_principle.min(2, ActivePrinciple)]
        def take(self): print("I took a drug with %s active principles" % len(self.active_principles))

print("classes: ", list(onto.classes()))

acetaminophen   = ActivePrinciple("acetaminophen")
amoxicillin     = ActivePrinciple("amoxicillin")
clavulanic_acid = ActivePrinciple("clavulanic_acid")

owlready2.AllDifferent([acetaminophen, amoxicillin, clavulanic_acid])

drug1 = Drug(active_principles = [acetaminophen])
drug2 = Drug(active_principles = [amoxicillin, clavulanic_acid])
drug3 = Drug(active_principles = [])

owlready2.close_world(Drug)

owlready2.sync_reasoner()

onto = onto_world.get_ontology("https://w3id.org/def/orka")