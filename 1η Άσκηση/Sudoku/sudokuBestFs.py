import itertools
import heapq

#---------- Sudoku 4x4 Setup ----------
ROWS = ['1','2','3','4']  #αριθμητική αρίθμηση από κάτω προς τα πάνω
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

#--------- Heuristic ----------
def heuristic(sol, unassigned):
    """Απλό ευρετικό: αριθμός μη ανατεθειμένων κελιών"""
    return len(unassigned)

#---------- Best-First Search with Forward Checking ----------
solutions = []
tree_nodes = 0
solution_leaves = 0
failure_leaves = 0

def best_first_search():
    global tree_nodes, solution_leaves, failure_leaves
    counter = itertools.count()  #μοναδικός αριθμός για heapq
    pq = []

    all_vars = set(domain.keys())
    assigned_vars = set(initial.keys())
    unassigned_vars = all_vars - assigned_vars
    sol0 = initial.copy()

    #αρχική κατάσταση
    heapq.heappush(pq, (heuristic(sol0, unassigned_vars), next(counter), sol0, unassigned_vars))

    while pq:
        h, _, sol, unassigned = heapq.heappop(pq)
        tree_nodes += 1

        if not unassigned:
            #βρήκαμε λύση
            solutions.append(sol.copy())
            solution_leaves += 1
            continue

        #MRV heuristic απλό: διάλεξε κελί με μικρότερο domain
        var = min(unassigned, key=lambda v: len(domain[v]))
        remaining = unassigned - {var}

        for value in domain[var]:
            if consistent(sol, var, value):
                new_sol = sol.copy()
                new_sol[var] = value
                heapq.heappush(pq, (heuristic(new_sol, remaining), next(counter), new_sol, remaining))
            else:
                failure_leaves += 1

#---------- Εκτέλεση ----------
best_first_search()

#---------- Εκτύπωση Αποτελεσμάτων ----------
print("\nΑΠΟΤΕΛΕΣΜΑΤΑ SUDOKU 4x4 ΜΕ BEST-FIRST SEARCH")
print("--------------------------------------------------")
for sol in solutions:
    full_sol = {(r,c): sol.get((r,c), '0') for r in ROWS for c in COLS}
    for r in reversed(ROWS):  # από κάτω προς τα πάνω
        print(' '.join(full_sol[(r,c)] for c in COLS))
    print('')  # κενή γραμμή μεταξύ λύσεων

print("Στατιστικά δέντρου αναζήτησης:")
print(f"Συνολικοί κόμβοι: {tree_nodes}")
print(f"Φύλλα λύσης: {solution_leaves}, Φύλλα αποτυχίας: {failure_leaves}")
