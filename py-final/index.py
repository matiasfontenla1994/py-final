import sqlite3
import os
from colorama import init, Fore, Style

init(autoreset=True)

DB_NAME = 'inventario.db'


# --- base de datos ---

def conectar_db():
    return sqlite3.connect(DB_NAME)

def inicializar_db():
    con = conectar_db()
    cur = con.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            descripcion TEXT,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            categoria TEXT
        )
    ''')
    con.commit()
    con.close()

def registrar_producto(nombre, descripcion, cantidad, precio, categoria):
    try:
        con = conectar_db()
        cur = con.cursor()
        cur.execute('''
            INSERT INTO productos (nombre, descripcion, cantidad, precio, categoria)
            VALUES (?, ?, ?, ?, ?)
        ''', (nombre, descripcion, cantidad, precio, categoria))
        con.commit()
        return True
    except sqlite3.Error as e:
        print(f"{Fore.RED}Error al registrar: {e}")
        return False
    finally:
        con.close()

def obtener_productos():
    con = conectar_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM productos")
    productos = cur.fetchall()
    con.close()
    return productos

def buscar_producto_por_id(id_producto):
    con = conectar_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM productos WHERE id = ?", (id_producto,))
    producto = cur.fetchone()
    con.close()
    return producto

def buscar_productos_por_criterio(criterio, valor):
    con = conectar_db()
    cur = con.cursor()
    query = f"SELECT * FROM productos WHERE {criterio} LIKE ?"
    cur.execute(query, (f"%{valor}%",))
    resultados = cur.fetchall()
    con.close()
    return resultados

def actualizar_producto(id_producto, campo, nuevo_valor):
    try:
        con = conectar_db()
        cur = con.cursor()
        query = f"UPDATE productos SET {campo} = ? WHERE id = ?"
        cur.execute(query, (nuevo_valor, id_producto))
        con.commit()
        return cur.rowcount > 0
    except sqlite3.Error as e:
        print(f"{Fore.RED}Error al actualizar: {e}")
        return False
    finally:
        con.close()

def eliminar_producto(id_producto):
    try:
        con = conectar_db()
        cur = con.cursor()
        cur.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
        con.commit()
        return cur.rowcount > 0
    except sqlite3.Error as e:
        print(f"{Fore.RED}Error al eliminar: {e}")
        return False
    finally:
        con.close()

def reporte_bajo_stock(limite):
    con = conectar_db()
    cur = con.cursor()
    cur.execute("SELECT * FROM productos WHERE cantidad <= ?", (limite,))
    productos = cur.fetchall()
    con.close()
    return productos


# --- interfaz ---

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_tabla_productos(productos):
    if not productos:
        print(f"{Fore.YELLOW}No se encontraron productos.")
        return

    print(f"\n{Fore.CYAN}{'ID':<5} | {'Nombre':<20} | {'Categoría':<15} | {'Precio':<10} | {'Stock':<8} | {'Descripción'}")
    print("-" * 80)
    for p in productos:
        print(f"{p[0]:<5} | {p[1]:<20} | {p[5]:<15} | ${p[4]:<9.2f} | {p[3]:<8} | {p[2]}")
    print("\n")

def menu_registrar():
    limpiar_pantalla()
    print(f"{Fore.GREEN}=== REGISTRAR NUEVO PRODUCTO ===\n")
    nombre = input("Nombre (obligatorio): ").strip()
    if not nombre:
        print(f"{Fore.RED}El nombre no puede estar vacio.")
        return

    descripcion = input("Descripcion: ").strip()

    try:
        cantidad = int(input("Cantidad (Stock): "))
        precio = float(input("Precio: "))
    except ValueError:
        print(f"{Fore.RED}Error: Cantidad debe ser entero y Precio debe ser un numero.")
        return

    categoria = input("Categoría: ").strip()

    if registrar_producto(nombre, descripcion, cantidad, precio, categoria):
        print(f"\n{Fore.GREEN}✔ Producto registrado exitosamente.")
    else:
        print(f"\n{Fore.RED} No se pudo registrar el producto.")

def menu_visualizar():
    limpiar_pantalla()
    print(f"{Fore.GREEN}=== INVENTARIO COMPLETO ===\n")
    productos = obtener_productos()
    mostrar_tabla_productos(productos)

def menu_buscar():
    limpiar_pantalla()
    print(f"{Fore.GREEN}=== BUSCAR PRODUCTOS ===\n")
    print("1. Buscar por ID")
    print("2. Buscar por Nombre")
    print("3. Buscar por Categoría")
    opcion = input("\nSeleccione opcion de busqueda: ")

    if opcion == "1":
        try:
            id_prod = int(input("Ingrese ID del producto: "))
            prod = buscar_producto_por_id(id_prod)
            mostrar_tabla_productos([prod] if prod else [])
        except ValueError:
            print(f"{Fore.RED}ID inválido.")
    elif opcion in ["2", "3"]:
        criterio = "nombre" if opcion == "2" else "categoria"
        valor = input(f"Ingrese el/la {criterio} a buscar: ").strip()
        resultados = buscar_productos_por_criterio(criterio, valor)
        mostrar_tabla_productos(resultados)
    else:
        print(f"{Fore.RED}Opcion no valida.")

def menu_actualizar():
    limpiar_pantalla()
    print(f"{Fore.GREEN}=== ACTUALIZAR PRODUCTO ===\n")
    try:
        id_prod = int(input("Ingrese el ID del producto que desea modificar: "))
    except ValueError:
        print(f"{Fore.RED}ID inválido.")
        return

    producto = buscar_producto_por_id(id_prod)
    if not producto:
        print(f"{Fore.RED}No existe ningún producto con el ID {id_prod}.")
        return

    print(f"\nProducto encontrado: {Fore.YELLOW}{producto[1]} (Categoría: {producto[5]})")
    print("¿Qué campo desea modificar?")
    print("1. Nombre\n2. Descripción\n3. Cantidad (Stock)\n4. Precio\n5. Categoría")

    opcion = input("\nSeleccione una opción: ")
    campos = {"1": "nombre", "2": "descripcion", "3": "cantidad", "4": "precio", "5": "categoria"}

    if opcion in campos:
        campo = campos[opcion]
        nuevo_valor = input(f"Ingrese el nuevo valor para {campo}: ").strip()

        if campo == "cantidad":
            try: nuevo_valor = int(nuevo_valor)
            except ValueError: print(f"{Fore.RED}Debe ser entero."); return
        elif campo == "precio":
            try: nuevo_valor = float(nuevo_valor)
            except ValueError: print(f"{Fore.RED}Debe ser un número real."); return
        elif campo == "nombre" and not nuevo_valor:
            print(f"{Fore.RED}El nombre no puede estar vacío.")
            return

        if actualizar_producto(id_prod, campo, nuevo_valor):
            print(f"\n{Fore.GREEN}✔ Producto actualizado correctamente.")
        else:
            print(f"\n{Fore.RED}✘ No se realizaron cambios.")
    else:
        print(f"{Fore.RED}Opción inválida.")

def menu_eliminar():
    limpiar_pantalla()
    print(f"{Fore.GREEN}=== ELIMINAR PRODUCTO ===\n")
    try:
        id_prod = int(input("Ingrese el ID del producto a eliminar: "))
    except ValueError:
        print(f"{Fore.RED}ID inválido.")
        return

    producto = buscar_producto_por_id(id_prod)
    if not producto:
        print(f"{Fore.RED}No se encontró el producto.")
        return

    confirmar = input(f"{Fore.RED}¿Está seguro de eliminar '{producto[1]}'? (s/n): ").lower()
    if confirmar == 's':
        if eliminar_producto(id_prod):
            print(f"\n{Fore.GREEN}✔ Producto eliminado con éxito.")
        else:
            print(f"\n{Fore.RED}✘ No se pudo eliminar.")
    else:
        print(f"\n{Fore.YELLOW}Operación cancelada.")

def menu_reporte():
    limpiar_pantalla()
    print(f"{Fore.GREEN}=== REPORTE: ALERTA DE STOCK BAJO ===\n")
    try:
        limite = int(input("Defina el límite máximo de stock para el reporte: "))
        productos = reporte_bajo_stock(limite)
        print(f"\n{Fore.YELLOW}Productos con stock igual o inferior a {limite}:")
        mostrar_tabla_productos(productos)
    except ValueError:
        print(f"{Fore.RED}Por favor, ingrese un número entero válido.")


# --- main ---

def main():
    inicializar_db()

    while True:
        print(f"{Fore.BLUE}{Style.BRIGHT}==========================================")
        print(f"{Fore.CYAN}{Style.BRIGHT}       SISTEMA DE GESTIÓN DE INVENTARIO    ")
        print(f"{Fore.BLUE}{Style.BRIGHT}==========================================")
        print("1. Registrar nuevo producto")
        print("2. Visualizar todos los productos")
        print("3. Buscar producto (Por ID, Nombre o Cat)")
        print("4. Actualizar datos de un producto")
        print("5. Eliminar un producto")
        print("6. Reporte de Stock Bajo")
        print(f"{Fore.RED}7. Salir")
        print(f"{Fore.BLUE}------------------------------------------")

        opcion = input("Seleccione una opción (1-7): ").strip()

        if opcion == "1":
            menu_registrar()
        elif opcion == "2":
            menu_visualizar()
        elif opcion == "3":
            menu_buscar()
        elif opcion == "4":
            menu_actualizar()
        elif opcion == "5":
            menu_eliminar()
        elif opcion == "6":
            menu_reporte()
        elif opcion == "7":
            print(f"\n{Fore.YELLOW}Saliendo del sistema... ¡Hasta luego!")
            break
        else:
            print(f"\n{Fore.RED}Opción no valida. Intente de nuevo.\n")

        input(f"{Fore.RESET}\nPresione Enter para continuar...")
        limpiar_pantalla()

if __name__ == "__main__":
    main()
