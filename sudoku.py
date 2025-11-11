import itertools as it

class SudokuCSP:
    def __init__(self, board_filepath):
        #1.Inicialización de Variables y Dominios.
        self.cols = "ABCDEFGHI"
        self.rows = range(1, 10) # 1-9

        # Generamos las claves de las celdas en un orden consistente.
        keys_product = list(it.product(self.rows, self.cols)) 
        self.cell_keys = [f"{key[1]}{key[0]}" for key in keys_product]

        # Cada celda puede tener un valor dominio del 1 al 9.
        self.var_doms = {key: set(range(1, 10)) for key in self.cell_keys}

        #2. Carga del Tablero Inicial desde Archivo.
        self.load_board(board_filepath)

        #Definimos los grupos de restricciones.
        #Combinamos todas las filas, columnas y cajas en una gran lista
        self.varsGroups = self._def_rows_constraints() + \
                          self._def_cols_constraints() + \
                          self._def_boxes_constraints()
        
        #4. Preparación de Restricciones 
        self.constraints = []
        for group in self.varsGroups:
            #Almacenamos las restricciones como tuplas (función, grupo de variables)
            self.constraints.append((self._all_dif, group))
            self.constraints.append((self._exc_value, group))

    def load_board(self, board_filepath):
        #Carga el estado inicial del tablero desde un archivo de texto.
        try:
            with open(board_filepath, 'r') as f:
                for key in self.cell_keys:
                    valor = f.readline().strip()
                    if valor.isdigit() and len(valor) == 1 and valor != '0':
                        # Si es un dígito válido, reducimos el dominio a solo ese valor
                        self.var_doms[key] = {int(valor)}
        except FileNotFoundError:
            print(f"Error: No se pudo encontrar el archivo del tablero: {board_filepath}")
        except Exception as e:
            print(f"Error al leer el tablero: {e}")

    #Métodos para definir grupos de restricciones:

    def _def_rows_constraints(self):
        RowsConstraints = []
        for i in self.rows:
            ConstraintVars = [f"{id}{i}" for id in self.cols]
            RowsConstraints.append(ConstraintVars)
        return RowsConstraints

    def _def_cols_constraints(self):
        ColsConstraints = []
        for id in self.cols:
            ConstraintVars = [f"{id}{i}" for i in self.rows]
            ColsConstraints.append(ConstraintVars)
        return ColsConstraints

    def _def_boxes_constraints(self):
        BoxesConstraints = []
        rows_list = list(self.rows) 
        for i in range(3):
            for j in range(3):
                ConstraintVars = []
                for x in range(3):
                    for y in range(3):
                        ConstraintVars.append(f"{self.cols[i*3+x]}{rows_list[j*3+y]}")
                BoxesConstraints.append(ConstraintVars)
        return BoxesConstraints

    #Métodos de Propagación de Restricciones:

    def _all_dif(self, vars_group):
        """
        Aplica la restricción 'All Different'.
        Si una celda tiene un solo valor, lo elimina de sus vecinas.
        """
        anyChange = False
        for var in vars_group:
            if len(self.var_doms[var]) == 1:
                val_to_remove = list(self.var_doms[var])[0]
                for var2 in vars_group:
                    if var != var2:
                        if val_to_remove in self.var_doms[var2]:
                            anyChange = True
                            self.var_doms[var2].discard(val_to_remove)
        return anyChange

    def _exc_value(self, vars_group):
        anyChange = False
        for var in vars_group:
            if len(self.var_doms[var]) > 1:
                A = self.var_doms[var]
                U = set()
                for var2 in vars_group:
                    if var != var2:
                        if len(self.var_doms[var2]) > 1:
                            U = U.union(self.var_doms[var2])
                Ex = A - U
                if len(Ex) == 1:
                    self.var_doms[var] = Ex
                    anyChange = True
        return anyChange

    #Método Solver

    def solve(self):
        #Ejecuta el bucle de propagación de restricciones hasta que no haya más cambios.
        iteration = 1
        while True:
            anyChange = False
            # Iteramos sobre las tuplas (funcion, grupo)
            for constraint_func, group_vars in self.constraints:
                # Llamamos a la función directamente (ej: self._all_dif(group_vars))
                anyChangeAux = constraint_func(group_vars)
                if anyChangeAux:
                    anyChange = True # Registramos si hubo *algún* cambio
            print(f"Iteración de propagación {iteration}")
            iteration += 1
            if anyChange == False:
                # Si no hubo cambios en una iteración completa, terminamos
                break
        
        print("Propagación de restricciones completada.")

    #Métodos Utilitarios

    def display(self):
        #Muestra el tablero de Sudoku en un formato legible en la consola.
        print("\nEstado actual del tablero:")
        for r in self.rows:
            if r in [4, 7]:
                print("------+-------+------") 
            line = ""
            for c in self.cols:
                if c in ['D', 'G']:
                    line += "| " 
                
                cell_domain = self.var_doms[f"{c}{r}"]
                if len(cell_domain) == 1:
                    line += f"{list(cell_domain)[0]} "
                else:
                    line += ". " 
            print(line)

    def is_solved(self):
        #Verifica si todas las celdas tienen un dominio de tamaño 1.
        for domain in self.var_doms.values():
            if len(domain) > 1:
                return False
        return True


if __name__ == "__main__":
    board_a_cargar = "board_moderado_prueba.txt" 

    # 1. Crear la instancia (esto carga el tablero y define las restricciones)
    print(f"\nCargando Sudoku desde '{board_a_cargar}'...")
    sudoku_game = SudokuCSP(board_filepath=board_a_cargar)
    
    print("Tablero Inicial:")
    sudoku_game.display()
    
    # 2. Resolver (aplicar propagación de restricciones)
    print("\nIniciando resolvedor (propagación de restricciones)...")
    sudoku_game.solve()
    
    # 3. Mostrar el resultado
    print("\nTablero Final (después de la propagación):")
    sudoku_game.display()
    
    if sudoku_game.is_solved():
        print("\n¡Sudoku Resuelto exitosamente solo con propagación!")
    else:
        print("\nPropagación completada. El Sudoku no se resolvió solo con esto.")
        print("Se necesitaría un algoritmo de Búsqueda (Backtracking) para terminarlo.")