import itertools

#---------- Sudoku 4x4 Setup ----------
ROWS = ['1','2','3','4']  #αριθμητική αρθροίση από κάτω προς τα πάνω
COLS = ['a','b','c','d']

#αρχική κατάσταση
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
    #μικρό τετράγωνο 2x2
    box_rows = ['1','2'] if r in ['1','2'] else ['3','4']
    box_cols = ['a','b'] if c in ['a','b'] else ['c','d']
    for br in box_rows:
        for bc in box_cols:
            if (br,bc) != var and sol.get((br,bc)) == value:
                return False
    return True

#---------- Forward Checking Search ----------
solutions = []
tree_nodes = 0
solution_leaves = 0
failure_leaves = 0

def forward_checking(sol, unassigned):
    global tree_nodes, solution_leaves, failure_leaves
    if not unassigned:
        #βρήκαμε λύση
        solutions.append(sol.copy())
        solution_leaves += 1
        tree_nodes += 1
        return True

    #διάλεξε επόμενο κελί (MRV heuristic απλό)
    var = min(unassigned, key=lambda v: len(domain[v]))
    remaining = unassigned - {var}

    tree_nodes += 1
    for value in domain[var]:
        if consistent(sol, var, value):
            sol[var] = value
            forward_checking(sol, remaining)
            sol.pop(var)
        else:
            #φύλλο αποτυχίας
            failure_leaves += 1

#---------- Εκτέλεση ----------
all_vars = set(domain.keys())
assigned_vars = set(initial.keys())
unassigned_vars = all_vars - assigned_vars
solution_dict = initial.copy()

forward_checking(solution_dict, unassigned_vars)

#--------- Εκτύπωση Αποτελεσμάτων ----------
print("\nΑΠΟΤΕΛΕΣΜΑΤΑ SUDOKU 4x4 ΜΕ FORWARD CHECKING")
print("--------------------------------------------------")
for sol in solutions:
    full_sol = {(r,c): sol.get((r,c), '0') for r in ROWS for c in COLS}
    for r in reversed(ROWS):  # από κάτω προς τα πάνω
        print(' '.join(full_sol[(r,c)] for c in COLS))
    print('')  #κενή γραμμή μεταξύ λύσεων

print("Στατιστικά δέντρου αναζήτησης:")
print(f"Συνολικοί κόμβοι: {tree_nodes}")
print(f"Φύλλα λύσης: {solution_leaves}, Φύλλα αποτυχίας: {failure_leaves}")
