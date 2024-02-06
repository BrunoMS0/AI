# -*- coding: utf-8 -*-
"""AI_Knowledge.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YROMZrvJZiNdfAcFqZYOyHMQbqFS1jSg
"""

import itertools

class Sentence():
    @classmethod
    def validate(cls,prep):
        #verify if the preposition is an instance of Sentence(), that will be right
        #if we define a preposition as a Symbol(), bc Symbol() inheritance of Sentence
        if isinstance(prep,Sentence):
            return True
        else:
            raise TypeError("The preposition must be a logic sentence")

    @classmethod
    def parenthesize(cls,prep):
        def balanced(prep):
            num = 0
            for i in prep:
                if(i==')'):num -= 1
                if(num == -1):return False
                if(i=='('): num += 1
            if(num == 0): return True

        if prep.isalpha() or not len(prep) or (prep[0]=='(' and prep[-1]==')' and balanced(prep[1:-1])):#start by the index 1 and finish in the penultimate index
            return prep
        else:
            return f"({prep})"

class Symbol(Sentence):
    def __init__(self,name):
        self.name = name

    def __eq__(self,other):
        return isinstance(other,Symbol) and self.name == other.name

    def __repr__(self):
        return self.name

    def evaluate(self,model):
        try:
            return model[self.name]
        except KeyError:
            raise EvaluationException(f"variable {self.name} not in model")

    def formula(self):
        return self.name

    def symbols(self):
        return {self.name}

class NOT(Sentence):
    def __init__(self,operand):
        Sentence.validate(operand)
        self.operand = operand

    def __eq__(self,other):#that works like an operator oveloading, "==" Overloading(sobrecargamos el ==)
        return isinstance(other,NOT) and self.operand == other.operand

    def __repr__(self):#"print() overloading(sobrecargamos la impresion)"
        return f"Not ({self.operand})"
        #remember the operator inside of NOT is a Symbol, so if we want to see the value inside
        #we have to implement the same method in Symbol()

    def formula(self):
        return "¬" + Sentence.parenthesize(self.operand.formula())

    def evaluate(self,model):
        return not self.operand.evaluate(model)

    def symbols(self):
        return self.operand.symbols()

class AND(Sentence):
    def __init__(self,*conjuncts):# "*" means it grab all argument that we give it, and store them in a variable "conjuncts"
        for conjunct in conjuncts:
            Sentence.validate(conjunct)
        self.conjuncts = list(conjuncts)

    def __eq__(self,other):
        return isinstance(other,AND) and self.conjuncts == other.conjuncts

    def __repr__(self):
        conjunctions = ",".join([str(conjunct) for conjunct in self.conjuncts])
        return f"AND({conjunctions})"

    def add(self,conjunct):
        Sentence.validate(conjunct)
        self.conjuncts.append(conjunct)


    def evaluate(self,model):
        return all(conjunct.evaluate(model) for conjunct in self.conjuncts)#all return True if all the subexpressions are True

    def formula(self):
        if len(self.conjuncts)==1:
            return self.conjuncts[0].formula()
        return " ∧ ".join([Sentence.parenthesize(conjunct.formula()) for conjunct in self.conjuncts])

    def symbols(self):
        return set.union(*[conjunct.symbols() for conjunct in self.conjuncts])#without union we would return more than 1 value
        #So we have to use union to gather the items, but union doesnt allowed a list of items, for that we need to separate it, so with "*"" we can do it

class OR(Sentence):
    def __init__(self,*disjuncts):# "*" means it grab all argument that we give it, and store them in a variable "conjuncts"
        for disjunct in disjuncts:
            Sentence.validate(disjunct)
        self.disjuncts = list(disjuncts)#list allows *elements

    def __eq__(self,other):
        return isinstance(other,OR) and self.disjuncts == other.disjuncts

    def __repr__(self):
        disjunctions = ",".join([str(disjunct) for disjunct in self.disjuncts])
        return f"OR({disjunctions})"

    def evaluate(self,model):
        return any(disjunct.evaluate(model) for disjunct in self.disjuncts)#all return False if all the subexpressions are False

    def formula(self):
        if len(self.disjuncts)==1:
            return self.disjuncts[0].formula()
        return " ∨ ".join([Sentence.parenthesize(disjunct.formula()) for disjunct in self.disjuncts])

    def symbols(self):
        return set.union(*[disjunct.symbols() for disjunct in self.disjuncts])

class IMPLICATION(Sentence):
    def __init__(self,antecedent,consequent):
        Sentence.validate(antecedent)
        Sentence.validate(consequent)
        self.implications = [antecedent,consequent]#[]array can be modified, ()tuple cannot be modified
    def __eq__(self,other):
        return isinstance(other,IMPLICATION) and self.implications == other.implicacions

    def __repr__(self):
        implications = ",".join([str(implication) for implication in self.implications])
        return f"IMPLICATION({implications})"

    def evaluate(self,model):
        return ((not(self.implications[0].evaluate(model))) or self.implications[1].evaluate(model))

    def formula(self):
        return "=>".join([Sentence.parenthesize(implication.formula()) for implication in self.implications])

    def symbols(self):
        return set.union(*[implication.symbols() for implication in self.implications])

class BICONDITIONAL(Sentence):
    def __init__(self,left,right):
        Sentence.validate(left)
        Sentence.validate(right)
        self.biconditionals = [left,right]#[]array can be modified, ()tuple cannot be modified
    def __eq__(self,other):
        return isinstance(other,BICONDITIONAL) and self.biconditionals == other.biconditionals

    def __repr__(self):
        biconditionals = ",".join([str(biconditional) for biconditional in self.biconditionals])
        return f"IMPLICATION({biconditionals})"

    def evaluate(self,model):
        left = self.biconditionals[0].evaluate(model)
        right = self.biconditionals[1].evaluate(model)
        return (left and right) or ((not left) and (not right))

    def formula(self):
        return "<=>".join([Sentence.parenthesize(biconditional.formula()) for biconditional in self.biconditionals])

    def symbols(self):
        return set.union(*[biconditional.symbols() for biconditional in self.biconditionals])

def model_check(knowledge,query):

    def check_all(knowledge, query, symbols, model):
        if not symbols:
            if knowledge.evaluate(model):
                return query.evaluate(model)
            return True
        else:
            remaining = symbols.copy()
            p = remaining.pop()

            model_true = model.copy()
            model_true[p] = True

            model_false = model.copy()
            model_false[p] = False

            return (check_all(knowledge,query,remaining,model_true) and check_all(knowledge,query,remaining,model_false))
            #We know the knowledge MUST BE TRUE...(1)

            #always there will be worlds where the prepositions make knowledge true, so in that worlds we have to return the value of the query
            #because if the query is TRUE all will be right but if the query is FALSE we have to know to establish a
            #"MAYBE(not sure that is TRUE so it will be FALSE)"

            #If the knowledge is FALSE, we know that is not posible for (1) so we have to return a TRUE value to not affect the results and the logic.
            #So we dont have to worry about the value of the query bc knowledge FALSE is not allowed. we only have to pay attention when the
            #knowledge is TRUE

            #the result of the recursion must be an AND bc we have to be sure that
            #in the "TRUE WORLDS" and in the "FALSE WORLDS",all the values are TRUE and "FALSE WORLDS"




    symbols = set.union(knowledge.symbols(),query.symbols())#union delete the repeated items

    return check_all(knowledge, query, symbols, dict())

rain = Symbol("rain")
hagrid = Symbol("hagrid")
dumbledore = Symbol("dumbledore")

sentence2 = AND(rain,hagrid,BICONDITIONAL(OR(dumbledore,NOT(rain)),IMPLICATION(AND(hagrid,rain),OR(rain,dumbledore))))
sentence4 = AND(IMPLICATION(AND(rain,NOT(hagrid)),dumbledore),rain,NOT(hagrid))

sentence5 = AND(IMPLICATION(rain,hagrid),rain)


print(sentence2.formula())
print(sentence4.formula())

print(model_check(sentence5,hagrid))

import termcolor

mustard = Symbol("ColMustard")
plum = Symbol("ProfPlum")
scarlet = Symbol("MsScarlet")
characters = [mustard, plum, scarlet]

ballroom = Symbol("ballroom")
kitchen = Symbol("kitchen")
library = Symbol("library")
rooms = [ballroom, kitchen, library]

knife = Symbol("knife")
revolver = Symbol("revolver")
wrench = Symbol("wrench")
weapons = [knife, revolver, wrench]

symbols = characters + rooms + weapons


def check_knowledge(knowledge):
    for symbol in symbols:
        if model_check(knowledge, symbol):#here verify if the symbol is only TRUE
            termcolor.cprint(f"{symbol}: YES", "green")
        elif not model_check(knowledge, NOT(symbol)):#here verify if the symbol is only FALSE
            print(f"{symbol}: MAYBE")#here only print if we dont know for sure what is the value of the symbol


# There must be a person, room, and weapon.
knowledge = AND(
    OR(mustard, plum, scarlet),
    OR(ballroom, kitchen, library),
    OR(knife, revolver, wrench)
)

# Initial cards
knowledge.add(AND(
    NOT(mustard), NOT(kitchen), NOT(revolver)
))

# Unknown card
knowledge.add(OR(
    NOT(scarlet), NOT(library), NOT(wrench)
))

# Known cards
knowledge.add(NOT(plum))
knowledge.add(NOT(ballroom))

check_knowledge(knowledge)

people = ["Gilderoy", "Pomona", "Minerva", "Horace"]
houses = ["Gryffindor", "Hufflepuff", "Ravenclaw", "Slytherin"]

symbols = []

knowledge = AND()

for person in people:
    for house in houses:
        symbols.append(Symbol(f"{person}{house}"))

for person in people:
    knowledge.add(OR(
        Symbol(f"{person}{houses[0]}"),
        Symbol(f"{person}{houses[1]}"),
        Symbol(f"{person}{houses[2]}"),
        Symbol(f"{person}{houses[3]}")
    ))

for person in people:
    for house_princ in houses:
        for house_aux in houses:
            if house_princ != house_aux:
                knowledge.add(
                    IMPLICATION(Symbol(f"{person}{house_princ}"),NOT(Symbol(f"{person}{house_aux}")))
                )

for house in houses:
    for person_princ in people:
        for person_aux in people:
            if person_princ != person_aux:
                knowledge.add(
                    IMPLICATION(Symbol(f"{person_princ}{house}"),NOT(Symbol(f"{person_aux}{house}")))
                )

knowledge.add(
    OR(Symbol("GilderoyGryffindor"), Symbol("GilderoyRavenclaw"))
)

knowledge.add(
    NOT(Symbol("PomonaSlytherin"))
)

knowledge.add(
    Symbol("MinervaGryffindor")
)

for symbol in symbols:
    if model_check(knowledge,symbol):
        print(symbol)