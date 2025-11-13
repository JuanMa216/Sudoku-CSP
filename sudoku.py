import itertools as it

class SudokuCSP:
    # Inicializa el tablero, sus variables y dominios.
    def __init__(self, board_filepath):
        """
        Inicializa el resolvedor de Sudoku.
        """
        #Definición de variables y dominios
        self.cols = "ABCDEFGHI" #Para las columnas A-I
        self.rows = range(1, 10) # 1-9 para las filas
        keys_product = list(it.product(self.rows, self.cols)) # (1, 'A'), (1, 'B')...
        self.cell_keys = [f"{key[1]}{key[0]}" for key in keys_product] # 'A1', 'B1'...
        self.var_doms = {key: set(range(1, 10)) for key in self.cell_keys} # Dominios iniciales 1-9

        self.load_board(board_filepath)
        #Definimos las restricciones para filas, columnas y cajas
        self.varsGroups = self._def_rows_constraints() + \
                          self._def_cols_constraints() + \
                          self._def_boxes_constraints()
        #Definimos las tuplas de restricciones.
        self.constraints = []
        for group in self.varsGroups:
            self.constraints.append((self._all_dif, group, "AllDif"))
            self.constraints.append((self._exc_value, group, "ExcVal"))
        #Cargamos el tablero desde el archivo
    def load_board(self, board_filepath):
        try:
            with open(board_filepath, 'r') as f: # Abrir el archivo en modo lectura, usamos 'with' para manejo seguro de archivos
                for key in self.cell_keys:
                    valor = f.readline().strip()
                    if valor.isdigit() and len(valor) == 1 and valor != '0':
                        self.var_doms[key] = {int(valor)}
        except FileNotFoundError:
            print(f"Error: No se pudo encontrar el archivo del tablero: {board_filepath}")
            exit() # Salir si el tablero no se puede cargar
        except Exception as e:
            print(f"Error al leer el tablero: {e}")
            exit()

    #Metodos para definir las restricciones del Sudoku

    def _def_rows_constraints(self): #Para las filas
        RowsConstraints = []
        for i in self.rows:
            ConstraintVars = [f"{id}{i}" for id in self.cols]
            RowsConstraints.append(ConstraintVars)
        return RowsConstraints

    def _def_cols_constraints(self): #Para las columnas
        ColsConstraints = []
        for id in self.cols:
            ConstraintVars = [f"{id}{i}" for i in self.rows]
            ColsConstraints.append(ConstraintVars)
        return ColsConstraints

    def _def_boxes_constraints(self): #Para las cajas 3x3
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

    #Métodos de Propagación de Restricciones 

    def _all_dif(self, vars_group, verbose):
        #Logica para la restricción 'All Different': Si una variable tiene un valor fijo,
        #ese valor se elimina de los dominios de las otras variables en el mismo grupo.
        anyChange = False
        for var in vars_group: # Iteramos sobre las variables en el grupo
            if len(self.var_doms[var]) == 1: # Si el dominio tiene un solo valor, es un valor fijo
                val_to_remove = list(self.var_doms[var])[0]
                # Impresión de depuración (verbose)
                if verbose:
                    print(f"  [AllDif] Variable {var} tiene valor fijo: {self.var_doms[var]}") # Mostrar valor fijo

                for var2 in vars_group: # Iteramos nuevamente para eliminar el valor de otras variables
                    if var != var2: # No nos comparamos con nosotros mismos
                        if val_to_remove in self.var_doms[var2]: # Si el valor está en el dominio de la otra variable
                            # Impresión de depuración (verbose)
                            if verbose: 
                                print(f"    -> Eliminando {val_to_remove} del dominio de {var2}. Dominio anterior: {self.var_doms[var2]}") # Mostrar dominio antes de la eliminación
                            self.var_doms[var2].discard(val_to_remove) # Elimina el valor del dominio
                            anyChange = True
        return anyChange # Retorna si hubo algún cambio en los dominios

    def _exc_value(self, vars_group, verbose):
        anyChange = False
        # Logica para la restricción 'Exclusive Value': Si un número solo puede ir en una celda de un grupo,
        # entonces esa celda debe tomar ese valor.
        # Contamos cuántas veces aparece cada número en los dominios del grupo
        for num in range(1, 10): # Iteramos sobre los números 1-9
            cells_with_num = []
            for var in vars_group: # Iteramos sobre las variables en el grupo
                if num in self.var_doms[var]: # Si el número está en el dominio de la variable
                    cells_with_num.append(var) # Añadimos la variable a la lista
            
            # Si un número solo aparece en el dominio de UNA celda...
            if len(cells_with_num) == 1:
                target_var = cells_with_num[0]
                # ...y esa celda aún no está resuelta
                if len(self.var_doms[target_var]) > 1: # Si la celda no está resuelta
                    new_domain = {num} # El nuevo dominio será solo ese número
                    # Impresión de depuración (verbose)
                    if verbose:
                        print(f"  [ExcVal] Valor {num} es exclusivo de la celda {target_var} en este grupo.")
                        print(f"    -> Dominio anterior: {self.var_doms[target_var]}. Nuevo dominio: {new_domain}")
                    self.var_doms[target_var] = new_domain # Actualizamos el dominio de la celda
                    anyChange = True
        return anyChange


    #Metodo Solver con verbose
    def Consistence(self, verbose):
        #Ejecuta el bucle de propagación de restricciones hasta que no haya más cambios.
        iteration = 1
        while True:
            anyChange = False
            # Iteramos sobre las tuplas (funcion, grupo, nombre)
            for constraint_func, group_vars, constraint_name in self.constraints:
                if verbose:
                    # Imprime el nombre de la restricción que se está aplicando
                    print(f"\nIter: {iteration} | Aplicando consistencia local: {constraint_name}") # Mostrar el nombre de la restricción
                # Llamamos a la función directamente (ej: self._all_dif(group_vars, verbose))
                anyChangeAux = constraint_func(group_vars, verbose) # Llamada a la función de restricción
                # Actualiza 'anyChange' si 'anyChangeAux' es True
                # (Usando 'or' como en tu captura de pantalla)
                anyChange = anyChangeAux or anyChange
            # Imprime el estado de los cambios al final de la iteración
            if verbose:
                print(f"\n--- Fin Iteración {iteration} ---")
                print(f"Hubo cambios en esta iteración: {anyChange}")
                # Pausa para revisión paso a paso
                input("Presiona Enter para continuar con la siguiente iteración...")
            
            iteration += 1
            
            if anyChange == False:
                # Si no hubo cambios en una iteración completa, terminamos
                break
        
        print(f"Propagación de restricciones completada después de {iteration - 1} iteraciones.")


    def solve(self, verbose=False):
        # Método principal para resolver el Sudoku usando propagación de restricciones.
        print("\nIniciando resolvedor (propagación de restricciones)...")
        self.Consistence(verbose)
        print("\nPropagación finalizada.")


    # --- Métodos Utilitarios ---

    def display(self):
        # Muestra el tablero de Sudoku en un formato legible en la consola.
        print("\nEstado actual del tablero:")
        # Itera sobre las filas (asumiendo que self.rows = range(1, 10))
        for r in self.rows:
            # Imprime el separador horizontal para las cajas
            if r in [4, 7]:
                print("------+-------+------") 
            
            line = ""
            # Itera sobre las columnas (asumiendo que self.cols = "ABCDEFGHI")
            for c in self.cols:
                # Imprime el separador vertical para las cajas
                if c in ['D', 'G']:
                    line += "| " 
                
                # Obtiene el dominio de la celda actual
                cell_domain = self.var_doms[f"{c}{r}"]
                
                # Si el dominio tiene 1 solo valor, es un valor fijo
                if len(cell_domain) == 1:
                    line += f"{list(cell_domain)[0]} "
                # Si el dominio tiene más de 1 valor, la celda no está resuelta
                else:
                    line += ". " # Punto para celdas sin resolver
            
            # Imprime la línea de la cuadrícula
            print(line)

    def is_solved(self):
        """
        Verifica si todas las celdas tienen un dominio de tamaño 1.
        """
        for domain in self.var_doms.values():
            if len(domain) > 1:
                return False
        return True


#Bloque para ejecutar el script directamente
if __name__ == "__main__":
    
    # Define el nombre del archivo que quieres cargar
    # Asegúrate de que esté en la misma carpeta que este script.
    board_a_cargar = "board_imposible_SD9TYJNO.txt" 

    # 1. Crear la instancia (esto carga el tablero y define las restricciones)
    print(f"\nCargando Sudoku desde '{board_a_cargar}'...")
    sudoku_game = SudokuCSP(board_filepath=board_a_cargar)
    
    print("Tablero Inicial:")
    sudoku_game.display()
    
    # 2. Resolver (aplicar propagación de restricciones)
    # --- MODIFICACIÓN ---
    # Cambia a verbose=True para ver el detalle de la propagación
    sudoku_game.solve(verbose=True) 
    
    # 3. Mostrar el resultado
    print("\nTablero Final (después de la propagación):")
    sudoku_game.display()
    
    if sudoku_game.is_solved():
        print("\n¡Sudoku Resuelto exitosamente solo con propagación!")
    else:
        print("\nPropagación completada. El Sudoku no se resolvió solo con esto.")
        print("Se necesitaría un algoritmo de Búsqueda (Backtracking) para terminarlo.")