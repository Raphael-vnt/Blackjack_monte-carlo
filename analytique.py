

#### ========================== CALCUL DE STRATEGIE OPTIMALE POUR SABOT INFINI ===============================  #####
## ----- --------- Règles supposées pour les calculs-------------------: 
# Hole_card = False,
# hit_after_ace_split =  False
# resplit_after_ace = False
# double_after_split =  True
# double_any_hand = True



import numpy as np 
import pandas as pd

map_to_Ace = {
              '11': 'A',
              '12': 'AA',
              '13': 'A2', 
              '14': 'A3',
              '15': 'A4', 
              '16': 'A5',     
              '17': 'A6', 
              '18': 'A7',
              '19': 'A8', 
              '20': 'A9',
              '21':'A10'   
            }

hand_to_value ={
    "0":'0', 
    "2":'2', 
    "3":'3', 
    "4":"4", 
    "5":"5", 
    "6":"6", 
    "7":"7", 
    "8":"8", 
    "9":"9", 
    "10":"10", 
    "10+":"10",
    "11":"11", 
    "12":"12", 
    "13":"13", 
    "14":"14", 
    "15":"15", 
    "16":"16", 
    "17":"17", 
    "18":"18", 
    "19":"19", 
    "20":"20",
    "21":"21",
    "22":"22", 
    "23":"23",
    "24":"24", 
    "25":"25",
    "26":"26",
    "27":"27",
    "28":"28",
    "29":"29",
    "30":"30",
    "A":"11", 
    "AA":"12", 
    "A2":"13", 
    "A3":"14", 
    "A4":"15", 
    "A5":"16", 
    "A6":"17", 
    "A7":"18", 
    "A8":"19", 
    "A9":"20",
    "A10" : "21"
}


carte_croupier = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "A"]
croupier_eg = ['17','18','19','20','21','A6','A7','A8','A9','A10']

inf_22 = ['0','2','3','4','5','6','7','8','9','10','10+','11','12','13','14','15','16','17','18','19','20','21','A','AA','A2','A3','A4','A5','A6','A7','A8','A9','A10']

# etats absorbants et non absorbants du joueur
etats_absorbants_j = ['21', '22', '23', '24', '25', 
                    '26', '27','28', '29', '30', 'A10']
etats_non_absorbants_j = [
    "0", "2", "3", "4", "5", "6", "7", "8", "9", "10", "10+",
    "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", 
    "A", "AA", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9"
]

# etats absorbants et non absorbants du croupier
etats_absorbants_c = ['17', '18', '19', '20', '21', '22', '23', '24', '25', 
                    '26', 'A6', 'A7',  'A8', 'A9','A10']
etats_non_absorbants_c = [
    "0", "2", "3", "4", "5", "6", "7", "8", "9", "10", "10+",
    "11", "12", "13", "14", "15", "16", "A", "AA", "A2", "A3", "A4", "A5"
]


def build_transition_matrix(proportions, matrix='j'):
    """
    Construit les matrices Q, R, I de la matrice canonique de transition P
    """
    
    if np.isclose(sum(proportions.values()), 1, atol=1e-08) == False : 
        return -1

    if matrix == 'j' : 
        absorbing_states = etats_absorbants_j
        transient_states = etats_non_absorbants_j
    else : 
        absorbing_states = etats_absorbants_c
        transient_states = etats_non_absorbants_c


    all_states = transient_states + absorbing_states
    n = len(all_states)
    m = len(transient_states)
    a = len(absorbing_states)

    idx = {s: i for i, s in enumerate(all_states)}

    def next_state(state, card):
            """Retourne l'état suivant après tirage d'une carte donnée."""
            hand = []
            if 'A' in state : 
                hand.append(state[0]) #A
                if len(state) >1 : 
                    hand.append(state[1])
            else : 
                hand.append(state)

            current_hand_value = hand_to_value[state] 
            if int(current_hand_value) >= 21 : 
                return state

            hand.append(card)

            nb_As = hand.count('A')
            hand_value = sum([11 if i== 'A' else 10 if i=='10+' else int(i) for i in hand])

            if 'A' in hand : 
                while nb_As > 0 and hand_value > 21 :
                    hand_value -= 10
                    nb_As -= 1
        
            if 'A' not in hand:
                if hand_value == 10 and state!= '0' : 
                    return '10+'
                return str(hand_value)
            
            if nb_As > 0 : 
                new_state = 'A' + str(hand_value - 11)

                if new_state == 'A10' and '10' not in hand : 
                    return '21'
                
                if hand == ['A', 'A'] : 
                    return 'AA'
                
                if '0' in hand : 
                    return 'A'

                return 'A' + str(hand_value - 11)
            
            return str(hand_value)

    P = np.zeros((n, n))

    for s in transient_states:
        for card, p in proportions.items():
            ns = next_state(s, card)
            P[idx[s], idx[ns]] += p

    Q = P[:m, :m]
    R = P[:m, m:]
    I = np.eye(a)
    O = np.zeros((R.shape[1], Q.shape[1]))  

    return Q, R, I, O


def get_B_croupier(proportions) : 
    """
    Matrice fondamentale du croupier
    """
    Q_t, R_t, I_t, O_t = build_transition_matrix(proportions, 'c')

    N_t = np.linalg.inv(np.eye(Q_t.shape[0]) - Q_t)
    B_t = N_t @ R_t

    B_df = pd.DataFrame(B_t, columns=etats_absorbants_c, index = etats_non_absorbants_c)
    B_df.index.name = 'Carte_croupier'
    B_df.columns.name = 'Arrivée croupier'

    return B_df


def get_P_joueur(proportions) : 
    """
    Matrice fondamentale du joueur
    """
    Q_t, R_t, I_t, O_t = build_transition_matrix(proportions, 'j')

    P_t = np.block([
    [Q_t, R_t],
    [O_t, I_t]
    ])

    P_df = pd.DataFrame(P_t, columns=etats_non_absorbants_j + etats_absorbants_j, index = etats_non_absorbants_j + etats_absorbants_j)
    P_df.index.name = 'Carte_joueur'
    P_df.columns.name = 'Arrivée_joueur'

    return P_df


def proba_win(player_hand, croupier_card, B, esperance=False):
    """
    Proba de victoire pour une main donnée (Stand), la carte du croupier, et la matrice B du croupier
    """
    p = sum(B.loc[croupier_card][['22', '23', '24', '25', '26']])

    num_player_hand = int(hand_to_value[player_hand])

    if num_player_hand > 21 : 
        return 0
    
    list_p = [str(item) for i in range(17, num_player_hand) for item in (i, map_to_Ace[str(i)])]
    
    if player_hand == 'A10':
        list_p.append('21')

    p+= sum(B.loc[croupier_card][list_p])

    if esperance ==True and player_hand == 'A10':
        p = p * 1.5
        
    return p


def proba_draw(player_hand, croupier_card, B):
    """
    Proba d'égalité pour une main donnée (Stand), la carte du croupier, et la matrice B du croupier
    """
    if player_hand not in croupier_eg : # SI pas au moins 17
        return 0
    
    # proba d'avoir égalité sur le soft + hard
    if player_hand != 'A10' and player_hand != '21' : 
        other = hand_to_value[player_hand] if (player_hand.startswith('A'))  else map_to_Ace[player_hand]
        return B.loc[croupier_card][player_hand] + B.loc[croupier_card][other]
    
    return B.loc[croupier_card][player_hand]


def proba_win_one_hit(player_hand, croupier_card, B, P_j, esperance=False, split=False):
    """
    Proba de victoire en tirant une seule fois (Hit), fonction de la carte du croupier, la matrice B du croupier, matrice P du joueur, presence du split ou non 
    """
    p_c_tau_sup_22 = sum(B.loc[croupier_card][['22', '23', '24', '25', '26']])
    p_tot = 0 

    for j in inf_22: ## j is next card

        p_j = P_j.loc[player_hand][j]
        if p_j <= 0 : 
            continue

        num_player_hand = int(hand_to_value[j])

        # list_p est la liste de cartes du croupier faisant gagner le joueur (hors bust)
        list_p = [str(item) for i in range(17, num_player_hand) for item in (i, map_to_Ace[str(i)])] 

        if j == 'A10' and split==False:
            list_p.append('21')

        # Proba d'avoir la carte suivante * Proba de win avec cette carte
        p_vnk = p_j * (p_c_tau_sup_22 + sum(B.loc[croupier_card][list_p]))
        
        if j == 'A10' and esperance==True:
            p_vnk = p_vnk * 1.5

        p_tot += p_vnk
        
    return p_tot


def proba_draw_one_hit(player_hand, croupier_card, B, P_j, split= False):
    """
    Proba d'égalité en tirant une seule fois (Hit), fonction de la carte du croupier, la matrice B du croupier, matrice P du joueur, presence du split ou non 
    """
    p_tot = 0
    for j in croupier_eg:

        if split == True and j == 'A10':
            # Si le joueur a A10 et split, la proba d'égalite est est la Proba de faire A10 * Proba que le croupier fasse 21
            p_tot += P_j.loc[player_hand][j] * B.loc[croupier_card]['21']

        else : 
            # Sinon juste proba d'avoir la meme carte
            p_tot += P_j.loc[player_hand][j] * B.loc[croupier_card][j] 
        
        if j != 'A10' and j != '21' : 
            # Si pas de A10 ou 21, la proba d'égalité est aussi l'autre possibilité (hard ou soft)
            other = hand_to_value[j] if (j.startswith('A'))  else map_to_Ace[j]
            p_tot += P_j.loc[player_hand][j] * B.loc[croupier_card][other]
            
    return p_tot


def proba_bust(player_hand, P):
    """
    Proba de bust si le joueur tire une seule fois (Hit) fontion de P
    """
    bust = ['22', '23', '24', '25', '26', '27', '28', '29', '30']
    p = 0
    for b in bust : 
        p +=  P.loc[player_hand][b]

    return p


def esperance_stand(player_hand, croupier_hand, B) :
    """
    Esperance du joueur lorsque ce dernier Stand face au croupier : 
    1.5 P(Blackjack) + 1. P(Win) - P(lose)
    """
    return proba_win(player_hand, croupier_hand, B, esperance=True) - (1 - proba_win(player_hand, croupier_hand, B)-  proba_draw(player_hand, croupier_hand, B))


def esperance_double(p_hand, c_hand, B, P, e=True, split=False ) :
    """
    Esperance du joueur lorsque ce dernier Hit une seule fois face au croupier : 
    e = False, split = True => Split, Pas de blackjack possible pour le joueur
    e = True, split = False => Pas de split, Cas classique
    """

    # Important à garder pour le split
    if p_hand == '21' or p_hand == 'A10': 
        return -2
    
    p_simple = proba_win_one_hit(p_hand, c_hand, B, P, esperance=e, split=split) - (1 - proba_win_one_hit(p_hand, c_hand, B, P, split=split) -  proba_draw_one_hit(p_hand, c_hand, B, P, split=split))
    return 2 * p_simple

## Attention faux pous un score de joueur = 21 (a modif et dans ce cas esperance de stand 21)
def MDP(croupier_card, B, P, gamma = 1.0, epsilon = 1e-8, return_delta = False):
    """
    Calcul de V, Q*, pi, selon la carte du croupier, la matrice B du croupier, la matrice P du joueur. 
    Seul Tirer ou Stand est possible
    """
    S = inf_22
    V = {s: 0.0 for s in S}
    pi = {s: 'S' for s in S}
    Q_star = {k: {'S':0, 'T':0} for k in S}

    A = ['S', 'T']
    c = croupier_card 
    iteration = 0

    epsilon = epsilon 
    gamma = gamma

    list_delta = []

    while True : 
        delta = 0
        V_new = V.copy()
        for s in S : 
            q_values = []
            for a in A : 
                r_s_a = esperance_stand(s, c, B) if a =='S' else - proba_bust(s, P)
                q = r_s_a
                if a  == 'T' : 
                    for s_ in S :
                        q +=  gamma * P.loc[s][s_]* V[s_]

                Q_star[s][a] = q        
                q_values.append(q)

            V_new[s] = max(q_values)
            
            if np.argmax(q_values)==1:
                pi[s]='T'
            else : 
                pi[s]='S'

            delta = max(delta, abs(V_new[s] - V[s]))
            
        V = V_new
        iteration += 1
        list_delta.append(delta)

        if delta < epsilon : 
            break
        

    if return_delta : 
        return V, Q_star, pi, list_delta

    return V, Q_star, pi, iteration


def get_all_esperance_hit(B, P) : 
    """
    Recup toutes les espérance de hit pour chaque couple (score joueur, carte croupier)
    """
    
    dic_esperance_hit = {k: {v: 0 for v in carte_croupier} for k in inf_22}

    for c in carte_croupier : 
        V, Q_star, pi, i = MDP(croupier_card=c, B=B, P=P)
        for j in inf_22 : 
            dic_esperance_hit[j][c] = Q_star[j]['T']
    
    return dic_esperance_hit


def esperance_split_new(p_hand, c_hand, B, P,  dic_esperance_hit, prop, k_split) :
    """
    Esperance de split
    """

    new_hand = None
    if p_hand == 'AA': 
        new_hand = 'A'
    elif p_hand == '20':
        new_hand = '10+'
    else : 
        new_hand = str(int(p_hand) //2)

    e = 0
    for s in inf_22 : 
         #proba de passer de new_hand ->> s
        p = P.loc[new_hand][s]
        
        if p <= 0:
            continue

        e_s = esperance_stand(s, c_hand, B) 

        if new_hand != 'A' :
            # Nouvelle main != As 

            #inclus 
            e_h = dic_esperance_hit[s][c_hand]
            e_d = esperance_double(s, c_hand, B, P, e=False, split=True)

        else : 
            # Nouvelle main = As
            if s == 'A10' : 
                e_s = esperance_stand('21', c_hand, B) 
                
            e_d = esperance_double(s, c_hand, B, P, e=False, split=True) 
            # On ne peut tirer qu'une seule fois
            e_h = e_d / 2

        e += p * max(e_s, e_h, e_d)
    
    if new_hand == 'A': ## Pas de splits suppplémentaires
        return 2 * e
    
    facteur = None
    q = prop[new_hand] if new_hand != '10+' else prop['10'] /4

    if k_split == np.inf : 
        facteur = 1 / (1 - q)
    else : 
        facteur = (1 - q**(k_split +1)) / (1 -q)

    
    return 2 * max(facteur *  e, e)


def get_choice_matrix(B, P, dic_esperance_hit, choice = 'hard'): 

    """
    Retourne la matrice de choix hard ou soft
    """

    carte_croupier = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "A"]

    if choice == 'hard' : 
        main_joueur_k = ['4', '5','6','7','8','9','10+','11','12','13','14','15','16','17','18','19','20']
    else : 
        main_joueur_k = ['AA', 'A2','A3','A4','A5','A6','A7','A8','A9']

    choice_matrix_hard_t = np.empty((len(main_joueur_k), len(carte_croupier)), dtype='<U20')
    max_e_matrix_hard_t= np.zeros((len(main_joueur_k), len(carte_croupier)))

    for i, m in enumerate(main_joueur_k) : 
        for j, c in enumerate(carte_croupier) :

            e_stand = esperance_stand(m, c, B) 
            e_hit = dic_esperance_hit[m][c]
            e_double = esperance_double(m, c, B, P)
            e_a = -0.5

            max_e = max(e_stand, e_hit, e_double, e_a)

            choice = ''
            if max_e == e_stand :
                choice = 'S'

            elif max_e == e_hit : 
                choice = 'H'
                
            elif max_e == e_double :
                other_max = max(e_stand, e_hit, e_a) 
                if other_max == e_stand : 
                    choice = 'Ds'
                elif other_max == e_hit : 
                    choice = 'Dh'
                else : 
                    choice = 'Da'
            else : 
                other_max = max(e_stand, e_hit, e_double)
                if other_max == e_stand : 
                    choice = 'As'
                elif other_max == e_hit : 
                    choice = 'Ah'
                else : 
                    choice = 'Ad'

            choice_matrix_hard_t[i][j] = choice
            max_e_matrix_hard_t[i][j] = max_e
    
    return choice_matrix_hard_t



def get_pair_matrix(B, P, dic_esperance_hit, prop, k_split) : 
    """
    Retourne la matrice de choix pairs
    """

    main_joueur_k = ['4','6','8','10','12','14','16','18','20','AA']
    carte_croupier = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "A"]

    choice_matrix_pair_t = np.empty((len(main_joueur_k), len(carte_croupier)), dtype='<U20')
    max_e_matrix_pair_t = np.zeros((len(main_joueur_k), len(carte_croupier)))

    for i, m in enumerate(main_joueur_k) : 
        for j, c in enumerate(carte_croupier) :

            e_stand = esperance_stand(m, c, B) 
            e_hit = dic_esperance_hit[m][c]
            e_double = esperance_double(m, c, B, P)
            e_split = esperance_split_new(m, c, B, P, dic_esperance_hit, prop, k_split)
            e_a = -0.5

            max_e = max(e_stand, e_hit, e_double, e_split, e_a)

            choice = ''
            if max_e == e_stand :
                choice = 'S'

            elif max_e == e_hit : 
                choice = 'H'

            elif max_e == e_split: 
                choice = 'SP'
                
            elif max_e == e_double :
                other_max = max(e_stand, e_hit, e_a) 
                if other_max == e_stand : 
                    choice = 'Ds'
                elif other_max == e_hit : 
                    choice = 'Dh'
                else : 
                    choice = 'Da'
            else : 
                other_max = max(e_stand, e_hit, e_double)
                if other_max == e_stand : 
                    choice = 'As'
                elif other_max == e_hit : 
                    choice = 'Ah'
                else : 
                    choice = 'Ad'

            choice_matrix_pair_t[i][j] = choice
            max_e_matrix_pair_t[i][j] = max_e
    
    return choice_matrix_pair_t


def color_cell(val):
    """
    Colorie df
    """
    colors = {
        "S": "background-color: lightcoral; color: lightred;",
        "H": "background-color: lightgreen;",

        "Dh": "background-color: lightblue;", 
        "Ds": "background-color: lightblue;",

        "Ah": "background-color: lightyellow;", 
        "As": "background-color: lightyellow;",

        "SP": "background-color: plum;"
    }
    return colors.get(val, "") 


def get_col_df(choix_array, choice = 'hard'):
     """
     Colorie la matrice de choix
     """ 
     if choice == 'hard' : 
        main_joueur_k = ['4', '5','6','7','8','9','10+','11','12','13','14','15','16','17','18','19','20']
     elif choice == 'soft': 
        main_joueur_k = ['AA', 'A2','A3','A4','A5','A6','A7','A8','A9']
     else : 
         main_joueur_k = ['4','6','8','10','12','14','16','18','20','AA']

     choix_t = pd.DataFrame(choix_array, index=main_joueur_k, columns=carte_croupier)
     choix_t.columns.name = "Carte croupier"
     choix_t.index.name = "Main joueur"

     choix_t = choix_t.style.map(color_cell)

     return choix_t


def transform_to_strategy(hard, soft, pair):
    """
    Transforme les matrices de choix en dictionnaire pour simu Monte Carlo
    """ 
    dealer_values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 'A']

    last_line = np.array([['S']*10])
    hard_ = np.vstack([hard, last_line])
    soft_ = np.vstack([soft, last_line])


    hard_ = np.char.upper(hard_)
    soft_ = np.char.upper(soft_)
    pair_ = np.char.upper(pair)

    hard_ = np.char.replace(hard_, 'A', 'R')
    soft_ = np.char.replace(soft_, 'A', 'R')
    pair_ = np.char.replace(pair_, 'A', 'R')
    pair_ = np.char.replace(pair_, 'SP', 'P')
  
   
    hard_values = list(range(4, 22))
    soft_values = list(range(12, 22))
    pair_values = list(range(2, 12))

    new_HARD = {}
    new_SOFT = {}
    new_PAIR = {}

    for i, pv in enumerate(hard_values):          
        for j, dv in enumerate(dealer_values):      
            new_HARD[(pv, dv)] = hard_[i, j]

    for i, pv in enumerate(soft_values):          
        for j, dv in enumerate(dealer_values):      
            new_SOFT[(pv, dv)] = soft_[i, j]

    for i, pv in enumerate(pair_values):          
        for j, dv in enumerate(dealer_values):      
            new_PAIR[(pv, dv)] = pair_[i, j]
    
    f_dic = {'HARD': new_HARD, 'SOFT': new_SOFT, 'PAIR': new_PAIR}

    return f_dic
