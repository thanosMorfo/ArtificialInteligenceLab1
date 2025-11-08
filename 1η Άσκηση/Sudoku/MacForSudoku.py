import itertools
from collections import deque
import copy

#---------- Sudoku 4x4 Setup ----------
ROWS = ['1','2','3','4']  # αριθμητική αρίθμηση από κάτω προς τα πάνω
COLS = ['a','b','c','d']

# αρχική κατάσταση
initial = {
    ('3','b'): '4',
    ('2','c'): '3',
    ('2','d'): '2',
    ('4','d'): '3'
}

#domain για κάθε κελί
domain = { (r,c): ['1','2','3','4'] if (r,c) not in initial else [initial[(r,c)]]
          for r in ROWS for c in COLS }

#---------- Constraints ----------
def consistent(sol, var, value):
    """Ελέγχει περιορισμούς για σειρά, στήλη και τετράγωνο 2x2"""
    r,c = var
    #σειρά
    for col in COLS:
        if col != c and sol.get((r,col)) == value:
            return False
    #στήλη
    for row in ROWS:
        if row != r and sol.get((row,c)) == value:
            return False
    # μικρό τετράγωνο 2x2
    box_rows = ['1','2'] if r in ['1','2'] else ['3','4']
    box_cols = ['a','b'] if c in ['a','b'] else ['c','d']
    for br in box_rows:
        for bc in box_cols:
            if (br,bc) != var and sol.get((br,bc)) == value:
                return False
    return True

#---------- MAC Helper Functions ----------
def revise(X, Y, domains):
    """Ελέγχει αν το domain της X μπορεί να παραμείνει συνεπές με το Y"""
    revised = False
    to_remove = []
    for x_val in domains[X]:
        #Υπάρχει έστω μία τιμή y στο domain του Y που δεν παραβιάζει τον περιορισμό;
        if not any(consistent({X: x_val, Y: y_val}, X, x_val) and consistent({X: x_val, Y: y_val}, Y, y_val)
                   for y_val in domains[Y]):
            to_remove.append(x_val)
            revised = True
    for val in to_remove:
        domains[X].remove(val)
    return revised

def ac3(domains, unassigned):
    """Διατηρεί arc-consistency σε όλα τα ζεύγη μεταβλητών"""
    queue = deque()
    for var1 in unassigned:
        for var2 in unassigned:
            if var1 != var2 and (var1[0]==var2[0] or var1[1]==var2[1] or same_box(var1,var2)):
                queue.append((var1,var2))
    while queue:
        X, Y = queue.popleft()
        if revise(X, Y, domains):
            if not domains[X]:
                return False
            for Z in unassigned:
                if Z != X and (X[0]==Z[0] or X[1]==Z[1] or same_box(X,Z)):
                    queue.append((Z,X))
    return True

def same_box(var1, var2):
    """Ελέγχει αν δύο κελιά ανήκουν στο ίδιο τετράγωνο 2x2"""
    r1, c1 = var1
    r2, c2 = var2
    box_rows1 = ['1','2'] if r1 in ['1','2'] else ['3','4']
    box_cols1 = ['a','b'] if c1 in ['a','b'] else ['c','d']
    return r2 in box_rows1 and c2 in box_cols1

#---------- MAC Search ----------
solutions = []
tree_nodes = 0
solution_leaves = 0
failure_leaves = 0

def mac_search(sol, unassigned, domains):
    global tree_nodes, solution_leaves, failure_leaves

    if not unassigned:
        # βρήκαμε λύση
        solutions.append(sol.copy())
        solution_leaves += 1
        tree_nodes += 1
        return True

    #διάλεξε μεταβλητή με MRV heuristic
    var = min(unassigned, key=lambda v: len(domains[v]))
    remaining = unassigned - {var}
    tree_nodes += 1

    for value in domains[var]:
        if consistent(sol, var, value):
            sol[var] = value
            new_domains = copy.deepcopy(domains)
            new_domains[var] = [value]

            # Εφαρμογή MAC
            if ac3(new_domains, remaining):
                mac_search(sol, remaining, new_domains)

            sol.pop(var)
        else:
            failure_leaves += 1

#---------- Εκτέλεση ----------
all_vars = set(domain.keys())
assigned_vars = set(initial.keys())
unassigned_vars = all_vars - assigned_vars
solution_dict = initial.copy()

mac_search(solution_dict, unassigned_vars, domain)

#---------- Εκτύπωση Αποτελεσμάτων ----------
print("\nΑΠΟΤΕΛΕΣΜΑΤΑ SUDOKU 4x4 ΜΕ MAC")
print("--------------------------------------------------")
for sol in solutions:
    full_sol = {(r,c): sol.get((r,c), '0') for r in ROWS for c in COLS}
    for r in reversed(ROWS):  # από κάτω προς τα πάνω
        print(' '.join(full_sol[(r,c)] for c in COLS))
    print('')  # κενή γραμμή μεταξύ λύσεων

print("Στατιστικά δέντρου αναζήτησης:")
print(f"Συνολικοί κόμβοι: {tree_nodes}")
print(f"Φύλλα λύσης: {solution_leaves}, Φύλλα αποτυχίας: {failure_leaves}")
