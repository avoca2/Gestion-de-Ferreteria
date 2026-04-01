#!/usr/bin/env python3
"""

Sistema de Gestión Ferretería Don Willy - Interfaz Gráfica Simplificada
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import sys
import os
import hashlib
import secrets

# Intentar importar Config
try:
    from config import Config
except ImportError as e:
    print(f"Error importando config: {e}")
    print("Creando config básica...")

class Config:
    SQLITE_DB_PATH = "don_willy.db"
    EMPRESA_NOMBRE = "FERRETERÍA DON WILLY"
    IVA_PORCENTAJE = 0.19
    PRIMARY_COLOR = "#2c3e50"
    SECONDARY_COLOR = "#3498db"
    SUCCESS_COLOR = "#27ae60"
    DANGER_COLOR = "#e74c3c"
    WARNING_COLOR = "#f39c12"
    LIGHT_BG = "#ecf0f1"
    DARK_TEXT = "#2c3e50"
    
    # Agregados para login
    ROLES = {
        'admin': 'Administrador',
        'cajero': 'Cajero/Vendedor',
        'inventario': 'Gestor de Inventario',
        'consulta': 'Solo Consulta'
    }
    
    PERMISOS = {
        'admin': ['productos', 'clientes', 'ventas', 'reportes', 'usuarios'],
        'cajero': ['ventas', 'clientes_consulta', 'productos_consulta'],
        'inventario': ['productos', 'reportes_inventario'],
        'consulta': ['productos_consulta', 'clientes_consulta', 'reportes_consulta']
    }
    
    @staticmethod
    def verificar_permiso(rol, permiso):
        if rol not in Config.PERMISOS:
            return False
        return permiso in Config.PERMISOS[rol]

class LoginWindow:
    """Ventana de inicio de sesión independiente"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{Config.EMPRESA_NOMBRE} - Login")
        self.root.geometry("400x400")
        self.root.configure(bg=Config.PRIMARY_COLOR)
        self.root.resizable(False, False)
        
        # Centrar ventana
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        self.usuario_autenticado = None
        self.create_widgets()
        
        # Hacer que la ventana sea modal
        self.root.grab_set()
    
    def create_widgets(self):
        """Crear widgets de login"""
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='white', padx=30, pady=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Logo/título
        tk.Label(main_frame, 
                text=Config.EMPRESA_NOMBRE,
                font=('Arial', 20, 'bold'),
                bg='white',
                fg=Config.PRIMARY_COLOR).pack(pady=(0, 20))
        
        tk.Label(main_frame, 
                text="Sistema de Gestión",
                font=('Arial', 12),
                bg='white',
                fg=Config.DARK_TEXT).pack(pady=(0, 20))
        
        # Formulario de login
        form_frame = tk.Frame(main_frame, bg='white')
        form_frame.pack(fill=tk.X, pady=10)
        
        # Usuario
        tk.Label(form_frame, 
                text="Usuario:",
                font=('Arial', 10, 'bold'),
                bg='white',
                anchor='w').pack(fill=tk.X, pady=(5, 2))
        
        self.username_var = tk.StringVar()
        self.entry_username = tk.Entry(form_frame, 
                                      textvariable=self.username_var,
                                      font=('Arial', 11),
                                      width=25)
        self.entry_username.pack(fill=tk.X, pady=(0, 10))
        self.entry_username.focus_set()
        self.entry_username.bind('<Return>', lambda e: self.entry_password.focus_set())
        
        # Contraseña
        tk.Label(form_frame, 
                text="Contraseña:",
                font=('Arial', 10, 'bold'),
                bg='white',
                anchor='w').pack(fill=tk.X, pady=(5, 2))
        
        self.password_var = tk.StringVar()
        self.entry_password = tk.Entry(form_frame, 
                                      textvariable=self.password_var,
                                      font=('Arial', 11),
                                      width=25,
                                      show="*")
        self.entry_password.pack(fill=tk.X, pady=(0, 20))
        self.entry_password.bind('<Return>', lambda e: self.login())
        
        # Botón de login
        self.btn_login = tk.Button(form_frame,
                                  text="INICIAR SESIÓN",
                                  command=self.login,
                                  bg=Config.SUCCESS_COLOR,
                                  fg='white',
                                  font=('Arial', 11, 'bold'),
                                  width=20,
                                  height=2)
        self.btn_login.pack(pady=10)
        
        # Estado
        self.label_status = tk.Label(main_frame,
                                    text="",
                                    font=('Arial', 9),
                                    bg='white',
                                    fg=Config.DANGER_COLOR)
        self.label_status.pack()
        
        # Información de acceso
        info_frame = tk.Frame(main_frame, bg='white')
        info_frame.pack(side=tk.BOTTOM, pady=10)
        tk.Label(info_frame,
                text="Usuario: admin | Contraseña: admin123",
                font=('Arial', 8),
                bg='white',
                fg=Config.PRIMARY_COLOR).pack()
        
        # Footer
        tk.Label(main_frame,
                text="© 2024 Ferretería Don Willy - Versión 1.0",
                font=('Arial', 8),
                bg='white',
                fg=Config.DARK_TEXT).pack(side=tk.BOTTOM, pady=10)
    
    def verificar_usuario(self, username, password):
        """Verificar credenciales de usuario"""
        conn = sqlite3.connect(Config.SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, username, password_hash, nombre_completo, rol, salt, activo 
                FROM usuarios 
                WHERE username = ? AND activo = 1
            """, (username,))
            
            usuario = cursor.fetchone()
            
            if usuario:
                # Verificar contraseña
                password_hash = hashlib.sha256((password + usuario['salt']).encode()).hexdigest()
                
                if password_hash == usuario['password_hash']:
                    # Actualizar último login
                    cursor.execute("""
                        UPDATE usuarios 
                        SET ultimo_login = CURRENT_TIMESTAMP 
                        WHERE id = ?
                    """, (usuario['id'],))
                    conn.commit()
                    
                    return {
                        'id': usuario['id'],
                        'username': usuario['username'],
                        'nombre_completo': usuario['nombre_completo'],
                        'rol': usuario['rol'],
                        'activo': usuario['activo']
                    }
            
            return None
            
        except Exception as e:
            print(f"Error al verificar usuario: {e}")
            return None
        finally:
            conn.close()
    
    def login(self):
        """Verificar credenciales"""
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        
        if not username or not password:
            self.label_status.config(text="Usuario y contraseña son obligatorios")
            return
        
        self.label_status.config(text="Verificando...")
        self.btn_login.config(state=tk.DISABLED)
        self.root.update()
        
        try:
            # Verificar usuario en la base de datos
            usuario = self.verificar_usuario(username, password)
            
            if usuario:
                self.usuario_autenticado = usuario
                self.root.destroy()  # Cerrar ventana de login
            else:
                self.label_status.config(text="Usuario o contraseña incorrectos")
                self.btn_login.config(state=tk.NORMAL)
                
        except Exception as e:
            self.label_status.config(text=f"Error: {str(e)}")
            self.btn_login.config(state=tk.NORMAL)
    
    def get_usuario(self):
        """Obtener usuario autenticado"""
        return self.usuario_autenticado
    
    def run(self):
        """Ejecutar la ventana de login"""
        self.root.mainloop()
        return self.usuario_autenticado

class SistemaFerreteriaGUI:
    def __init__(self, root, usuario):
        self.root = root
        self.usuario = usuario
        self.root.title(f"{Config.EMPRESA_NOMBRE} - Sistema de Gestión [{usuario['rol'].upper()}]")
        self.root.geometry("1100x650")
        self.root.configure(bg=Config.LIGHT_BG)
        
        # Inicializar base de datos
        self.init_database()
        
        # Variables para el carrito
        self.carrito = []
        
        # Crear interfaz
        self.create_widgets()
        
        # Cargar datos iniciales según permisos
        if self.tiene_permiso('productos_consulta'):
            self.cargar_productos()
        
        if self.tiene_permiso('clientes_consulta'):
            self.cargar_clientes()
        
        if self.tiene_permiso('reportes_consulta'):
            self.actualizar_reportes()
    
    def tiene_permiso(self, permiso):
        """Verificar si el usuario tiene un permiso específico"""
        return Config.verificar_permiso(self.usuario['rol'], permiso)
    
    def init_database(self):
        """Inicializar base de datos"""
        self.conn = sqlite3.connect(Config.SQLITE_DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
    
    def create_widgets(self):
        """Crear todos los widgets de la interfaz según permisos"""
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Barra superior con información de usuario
        top_bar = tk.Frame(main_frame, bg=Config.PRIMARY_COLOR, height=40)
        top_bar.pack(fill=tk.X, pady=(0, 10))
        top_bar.pack_propagate(False)
        
        # Información del usuario
        user_info = f"{self.usuario['nombre_completo']} ({Config.ROLES[self.usuario['rol']]})"
        tk.Label(top_bar, 
                text=user_info,
                bg=Config.PRIMARY_COLOR,
                fg='white',
                font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)
        
        # Botón de cerrar sesión
        tk.Button(top_bar,
                 text="Cerrar Sesión",
                 command=self.cerrar_sesion,
                 bg=Config.DANGER_COLOR,
                 fg='white',
                 font=('Arial', 9)).pack(side=tk.RIGHT, padx=10)
        
        # Título
        title_label = tk.Label(main_frame,
                              text=Config.EMPRESA_NOMBRE,
                              font=('Arial', 20, 'bold'),
                              bg=Config.PRIMARY_COLOR,
                              fg='white')
        title_label.pack(fill=tk.X, pady=(0, 20), ipady=10)
        
        # Notebook (pestañas) - Solo mostrar pestañas según permisos
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Crear las pestañas según permisos
        if self.tiene_permiso('productos'):
            self.create_tab_productos(editable=True)
        elif self.tiene_permiso('productos_consulta'):
            self.create_tab_productos(editable=False)
        
        if self.tiene_permiso('clientes'):
            self.create_tab_clientes(editable=True)
        elif self.tiene_permiso('clientes_consulta'):
            self.create_tab_clientes(editable=False)
        
        if self.tiene_permiso('ventas'):
            self.create_tab_ventas()
        
        if self.tiene_permiso('reportes') or self.tiene_permiso('reportes_consulta'):
            self.create_tab_reportes()
        
        if self.tiene_permiso('usuarios') and self.usuario['rol'] == 'admin':
            self.create_tab_usuarios()
        
        # Barra de estado
        status_text = f"Usuario: {self.usuario['nombre_completo']} | Rol: {Config.ROLES[self.usuario['rol']]} | Sistema Don Willy Ferretería"
        self.status_bar = tk.Label(self.root,
                                  text=status_text,
                                  bg=Config.PRIMARY_COLOR,
                                  fg='white',
                                  anchor=tk.W,
                                  relief=tk.SUNKEN)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def cerrar_sesion(self):
        """Cerrar sesión y volver al login"""
        self.conn.close()
        self.root.destroy()
        main()  # Reiniciar la aplicación
    
    def create_tab_productos(self, editable=True):
        """Crear pestaña de productos"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📦 Productos")
        
        # Frame superior (botones)
        top_frame = ttk.Frame(tab)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Solo mostrar botones de edición si tiene permisos
        if editable:
            tk.Button(top_frame, text="➕ Nuevo",
                     command=self.nuevo_producto,
                     bg=Config.SUCCESS_COLOR,
                     fg='white',
                     font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
            
            tk.Button(top_frame, text="✏️ Editar",
                     command=self.editar_producto,
                     bg=Config.WARNING_COLOR,
                     fg='white',
                     font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
            
            tk.Button(top_frame, text="🗑️ Eliminar",
                     command=self.eliminar_producto,
                     bg=Config.DANGER_COLOR,
                     fg='white',
                     font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        # Botón de actualizar siempre visible
        tk.Button(top_frame if editable else tab, text="🔄 Actualizar",
                 command=self.cargar_productos,
                 bg=Config.SECONDARY_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT if editable else tk.TOP, 
                                        padx=5, 
                                        pady=(0, 10) if not editable else 0)
        
        # Frame de búsqueda
        search_frame = tk.Frame(tab)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(search_frame, text="Buscar:",
                font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        self.producto_search = tk.Entry(search_frame, width=40, font=('Arial', 10))
        self.producto_search.pack(side=tk.LEFT, padx=5)
        self.producto_search.bind('<KeyRelease>', self.buscar_productos)
        
        # Treeview para productos - CORREGIDO: usar ttk.Treeview
        frame_tree = ttk.Frame(tab)
        frame_tree.pack(fill=tk.BOTH, expand=True)
        
        columns = ('ID', 'Código', 'Nombre', 'Categoría', 'Precio', 'Stock', 'Mínimo')
        self.tree_productos = ttk.Treeview(frame_tree, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        for col in columns:
            self.tree_productos.heading(col, text=col)
            width = 80
            if col == 'Nombre': width = 200
            if col == 'ID': width = 50
            self.tree_productos.column(col, width=width, minwidth=50)
        
        # Scrollbars
        vsb = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree_productos.yview)
        hsb = ttk.Scrollbar(frame_tree, orient="horizontal", command=self.tree_productos.xview)
        self.tree_productos.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout
        self.tree_productos.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        frame_tree.grid_rowconfigure(0, weight=1)
        frame_tree.grid_columnconfigure(0, weight=1)
        
        # Info
        self.label_info_productos = tk.Label(tab, text="Total productos: 0",
                                           font=('Arial', 10, 'bold'),
                                           bg=Config.LIGHT_BG)
        self.label_info_productos.pack(pady=10)

    def create_tab_clientes(self, editable=True):
        """Crear pestaña de clientes"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="👥 Clientes")
        
        # Frame superior
        top_frame = ttk.Frame(tab)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Solo mostrar botones de edición si tiene permisos
        if editable:
            tk.Button(top_frame, text="➕ Nuevo",
                     command=self.nuevo_cliente,
                     bg=Config.SUCCESS_COLOR,
                     fg='white',
                     font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
            
            tk.Button(top_frame, text="✏️ Editar",
                     command=self.editar_cliente,
                     bg=Config.WARNING_COLOR,
                     fg='white',
                     font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
            
            tk.Button(top_frame, text="🗑️ Eliminar",
                     command=self.eliminar_cliente,
                     bg=Config.DANGER_COLOR,
                     fg='white',
                     font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        # Botón de actualizar siempre visible
        tk.Button(top_frame if editable else tab, text="🔄 Actualizar",
                 command=self.cargar_clientes,
                 bg=Config.SECONDARY_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT if editable else tk.TOP, 
                                        padx=5, 
                                        pady=(0, 10) if not editable else 0)
        
        # Treeview para clientes - CORREGIDO: usar ttk.Treeview
        frame_tree = ttk.Frame(tab)
        frame_tree.pack(fill=tk.BOTH, expand=True)
        
        columns = ('ID', 'RUT', 'Nombre', 'Teléfono', 'Email', 'Tipo')
        self.tree_clientes = ttk.Treeview(frame_tree, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree_clientes.heading(col, text=col)
            width = 100
            if col == 'Nombre': width = 150
            if col == 'Email': width = 150
            if col == 'ID': width = 50
            self.tree_clientes.column(col, width=width)
        
        # Scrollbars
        vsb = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree_clientes.yview)
        hsb = ttk.Scrollbar(frame_tree, orient="horizontal", command=self.tree_clientes.xview)
        self.tree_clientes.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree_clientes.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        frame_tree.grid_rowconfigure(0, weight=1)
        frame_tree.grid_columnconfigure(0, weight=1)
        
        # Info
        self.label_info_clientes = tk.Label(tab, text="Total clientes: 0",
                                          font=('Arial', 10, 'bold'),
                                          bg=Config.LIGHT_BG)
        self.label_info_clientes.pack(pady=10)

    def create_tab_ventas(self):
        """Crear pestaña de ventas"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="💰 Ventas")
        
        # Dividir en dos frames
        left_frame = ttk.Frame(tab)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_frame = ttk.Frame(tab)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # === LADO IZQUIERDO: Productos ===
        tk.Label(left_frame, text="🛒 Productos Disponibles",
                font=('Arial', 12, 'bold'),
                bg=Config.LIGHT_BG).pack(pady=(0, 10))
        
        # Búsqueda
        search_frame = tk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(search_frame, text="Buscar:").pack(side=tk.LEFT)
        self.search_venta = tk.Entry(search_frame, width=30)
        self.search_venta.pack(side=tk.LEFT, padx=5)
        self.search_venta.bind('<KeyRelease>', self.buscar_productos_venta)
        
        # Lista de productos - CORREGIDO: usar ttk.Treeview
        frame_tree = ttk.Frame(left_frame)
        frame_tree.pack(fill=tk.BOTH, expand=True)
        
        columns = ('ID', 'Producto', 'Precio', 'Stock')
        self.tree_productos_venta = ttk.Treeview(frame_tree, columns=columns, show='headings', height=12)
        
        for col in columns:
            self.tree_productos_venta.heading(col, text=col)
            width = 80
            if col == 'Producto': width = 150
            self.tree_productos_venta.column(col, width=width)
        
        vsb = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree_productos_venta.yview)
        self.tree_productos_venta.configure(yscrollcommand=vsb.set)
        
        self.tree_productos_venta.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        
        frame_tree.grid_rowconfigure(0, weight=1)
        frame_tree.grid_columnconfigure(0, weight=1)
        
        # Botón para agregar al carrito
        tk.Button(left_frame, text="➕ Agregar al Carrito",
                 command=self.agregar_al_carrito,
                 bg=Config.SUCCESS_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(pady=10)
        
        # === LADO DERECHO: Carrito ===
        tk.Label(right_frame, text="🛍️ Carrito de Compra",
                font=('Arial', 12, 'bold'),
                bg=Config.LIGHT_BG).pack(pady=(0, 10))
        
        # Treeview del carrito - CORREGIDO: usar ttk.Treeview
        frame_tree_carrito = ttk.Frame(right_frame)
        frame_tree_carrito.pack(fill=tk.BOTH, expand=True)
        
        columns_carrito = ('Producto', 'Cantidad', 'Precio', 'Total')
        self.tree_carrito = ttk.Treeview(frame_tree_carrito, columns=columns_carrito, show="headings", height=10)
        
        for col in columns_carrito:
            self.tree_carrito.heading(col, text=col)
            self.tree_carrito.column(col, width=90)
        
        vsb_carrito = ttk.Scrollbar(frame_tree_carrito, orient="vertical", command=self.tree_carrito.yview)
        self.tree_carrito.configure(yscrollcommand=vsb_carrito.set)
        
        self.tree_carrito.grid(row=0, column=0, sticky='nsew')
        vsb_carrito.grid(row=0, column=1, sticky='ns')
        
        frame_tree_carrito.grid_rowconfigure(0, weight=1)
        frame_tree_carrito.grid_columnconfigure(0, weight=1)
        
        # Botones del carrito
        btn_frame = tk.Frame(right_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(btn_frame, text="➖ Quitar",
                 command=self.quitar_del_carrito,
                 bg=Config.WARNING_COLOR,
                 fg='white',
                 font=('Arial', 9)).pack(side=tk.LEFT, padx=2)
        
        tk.Button(btn_frame, text="🗑️ Vaciar",
                 command=self.vaciar_carrito,
                 bg=Config.DANGER_COLOR,
                 fg='white',
                 font=('Arial', 9)).pack(side=tk.LEFT, padx=2)
        
        # Totales
        total_frame = tk.Frame(right_frame, bg=Config.LIGHT_BG)
        total_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(total_frame, text="Subtotal:",
                font=('Arial', 10, 'bold'),
                bg=Config.LIGHT_BG).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.label_subtotal = tk.Label(total_frame, text="$0", font=('Arial', 10), bg=Config.LIGHT_BG)
        self.label_subtotal.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        tk.Label(total_frame, text=f"IVA ({Config.IVA_PORCENTAJE*100}%):",
                font=('Arial', 10, 'bold'),
                bg=Config.LIGHT_BG).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.label_iva = tk.Label(total_frame, text="$0", font=('Arial', 10), bg=Config.LIGHT_BG)
        self.label_iva.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        tk.Label(total_frame, text="TOTAL:",
                font=('Arial', 11, 'bold'),
                bg=Config.LIGHT_BG).grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.label_total = tk.Label(total_frame, text="$0",
                                   font=('Arial', 11, 'bold'),
                                   fg=Config.SUCCESS_COLOR,
                                   bg=Config.LIGHT_BG)
        self.label_total.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Botón finalizar venta
        tk.Button(right_frame, text="✅ FINALIZAR VENTA",
                 command=self.finalizar_venta,
                 bg=Config.SUCCESS_COLOR,
                 fg='white',
                 font=('Arial', 12, 'bold'),
                 height=2).pack(fill=tk.X, pady=10)

    def create_tab_reportes(self):
        """Crear pestaña de reportes"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📊 Reportes")
        
        # Frame para estadísticas
        stats_frame = tk.LabelFrame(tab, text="📈 Estadísticas Generales",
                                   font=('Arial', 11, 'bold'),
                                   bg=Config.LIGHT_BG,
                                   padx=10, pady=10)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Crear grid para estadísticas
        grid_frame = tk.Frame(stats_frame, bg=Config.LIGHT_BG)
        grid_frame.pack(fill=tk.BOTH, expand=True)
        
        # Estadísticas
        self.label_total_productos = tk.Label(grid_frame,
                                            text="Total Productos: Cargando...",
                                            font=('Arial', 10, 'bold'),
                                            bg=Config.LIGHT_BG)
        self.label_total_productos.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        
        self.label_productos_bajo = tk.Label(grid_frame,
                                           text="Productos con Stock Bajo: Cargando...",
                                           font=('Arial', 10, 'bold'),
                                           bg=Config.LIGHT_BG)
        self.label_productos_bajo.grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        
        self.label_total_clientes = tk.Label(grid_frame,
                                           text="Total Clientes: Cargando...",
                                           font=('Arial', 10, 'bold'),
                                           bg=Config.LIGHT_BG)
        self.label_total_clientes.grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        
        self.label_ventas_hoy = tk.Label(grid_frame,
                                        text="Ventas Hoy: Cargando...",
                                        font=('Arial', 10, 'bold'),
                                        bg=Config.LIGHT_BG)
        self.label_ventas_hoy.grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        
        # Botón para actualizar
        tk.Button(stats_frame, text="🔄 Actualizar Reportes",
                 command=self.actualizar_reportes,
                 bg=Config.SECONDARY_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(pady=10)

    def create_tab_usuarios(self):
        """Crear pestaña de gestión de usuarios (solo admin)"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="👤 Usuarios")
        
        # Frame superior
        top_frame = ttk.Frame(tab)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(top_frame, text="➕ Nuevo Usuario",
                 command=self.nuevo_usuario,
                 bg=Config.SUCCESS_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(top_frame, text="✏️ Editar",
                 command=self.editar_usuario,
                 bg=Config.WARNING_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(top_frame, text="🗑️ Eliminar",
                 command=self.eliminar_usuario,
                 bg=Config.DANGER_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        tk.Button(top_frame, text="🔄 Actualizar",
                 command=self.cargar_usuarios,
                 bg=Config.SECONDARY_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        
        # Treeview para usuarios - CORREGIDO: usar ttk.Treeview
        frame_tree = ttk.Frame(tab)
        frame_tree.pack(fill=tk.BOTH, expand=True)
        
        columns = ('ID', 'Username', 'Nombre', 'Email', 'Rol', 'Activo', 'Último Login')
        self.tree_usuarios = ttk.Treeview(frame_tree, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.tree_usuarios.heading(col, text=col)
            width = 100
            if col == 'Nombre': width = 150
            if col == 'Email': width = 150
            if col == 'Último Login': width = 120
            self.tree_usuarios.column(col, width=width)
        
        # Scrollbars
        vsb = ttk.Scrollbar(frame_tree, orient="vertical", command=self.tree_usuarios.yview)
        hsb = ttk.Scrollbar(frame_tree, orient="horizontal", command=self.tree_usuarios.xview)
        self.tree_usuarios.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree_usuarios.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        frame_tree.grid_rowconfigure(0, weight=1)
        frame_tree.grid_columnconfigure(0, weight=1)
        
        # Info
        self.label_info_usuarios = tk.Label(tab, text="Total usuarios: 0",
                                          font=('Arial', 10, 'bold'),
                                          bg=Config.LIGHT_BG)
        self.label_info_usuarios.pack(pady=10)
        
        # Cargar usuarios
        self.cargar_usuarios()

    # --- MÉTODOS PARA PRODUCTOS ---
    
    def cargar_productos(self, search_term=""):
        """Cargar productos en el Treeview"""
        # Limpiar treeview
        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)
        
        try:
            # Consultar productos
            if search_term:
                query = "SELECT * FROM productos WHERE nombre LIKE ? OR codigo LIKE ? ORDER BY nombre"
                params = (f'%{search_term}%', f'%{search_term}%')
            else:
                query = "SELECT * FROM productos ORDER BY nombre"
                params = ()
            
            self.cursor.execute(query, params)
            productos = self.cursor.fetchall()
            
            # Insertar en treeview
            for producto in productos:
                self.tree_productos.insert("", tk.END, values=(
                    producto['id'],
                    producto['codigo'],
                    producto['nombre'],
                    producto['categoria'],
                    f"${producto['precio_venta']:,.0f}",
                    producto['stock'],
                    producto['stock_minimo']
                ))
            
            # Actualizar información
            self.label_info_productos.config(text=f"Total productos: {len(productos)}")
            
            # También cargar en pestaña de ventas
            self.buscar_productos_venta()
            
        except Exception as e:
            print(f"Error al cargar productos: {e}")

    def buscar_productos(self, event=None):
        """Buscar productos según término"""
        search_term = self.producto_search.get()
        self.cargar_productos(search_term)

    def nuevo_producto(self):
        """Abrir formulario para nuevo producto"""
        if not self.tiene_permiso('productos'):
            messagebox.showwarning("Permiso Denegado", "No tiene permisos para crear productos")
            return
        
        self.dialogo_producto(None)

    def editar_producto(self):
        """Editar producto seleccionado"""
        if not self.tiene_permiso('productos'):
            messagebox.showwarning("Permiso Denegado", "No tiene permisos para editar productos")
            return
        
        selection = self.tree_productos.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un producto para editar")
            return
        
        item = self.tree_productos.item(selection[0])
        producto_id = item['values'][0]
        
        # Obtener datos del producto
        self.cursor.execute("SELECT * FROM productos WHERE id = ?", (producto_id,))
        producto = self.cursor.fetchone()
        
        if producto:
            self.dialogo_producto(producto)

    def eliminar_producto(self):
        """Eliminar producto seleccionado"""
        if not self.tiene_permiso('productos'):
            messagebox.showwarning("Permiso Denegado", "No tiene permisos para eliminar productos")
            return
        
        selection = self.tree_productos.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un producto para eliminar")
            return
        
        item = self.tree_productos.item(selection[0])
        producto_id = item['values'][0]
        producto_nombre = item['values'][2]
        
        respuesta = messagebox.askyesno("Confirmar",
                                       f"¿Eliminar el producto: {producto_nombre}?")
        
        if respuesta:
            try:
                self.cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
                self.conn.commit()
                self.cargar_productos()
                self.actualizar_reportes()
                messagebox.showinfo("Éxito", "Producto eliminado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")

    def dialogo_producto(self, producto):
        """Diálogo para agregar/editar producto"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Nuevo Producto" if producto is None else "Editar Producto")
        dialog.geometry("500x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        main_frame = tk.Frame(dialog, bg=Config.LIGHT_BG, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Campos del formulario
        campos = [
            ("Código:", "codigo", 0),
            ("Nombre:", "nombre", 1),
            ("Descripción:", "descripcion", 2),
            ("Categoría:", "categoria", 3),
            ("Precio Compra:", "precio_compra", 4),
            ("Precio Venta:", "precio_venta", 5),
            ("Stock:", "stock", 6),
            ("Stock Mínimo:", "stock_minimo", 7),
            ("Proveedor:", "proveedor", 8)
        ]
        
        entries = {}
        
        for label_text, field_name, row in campos:
            tk.Label(main_frame, text=label_text, bg=Config.LIGHT_BG).grid(row=row, column=0, sticky=tk.W, pady=5)
            
            if field_name == 'descripcion':
                entry = tk.Text(main_frame, height=4, width=40)
                entry.grid(row=row, column=1, pady=5)
            else:
                entry = tk.Entry(main_frame, width=40)
                entry.grid(row=row, column=1, pady=5)
            
            entries[field_name] = entry
        
        # Si hay datos, llenar campos
        if producto:
            for field_name, entry in entries.items():
                if field_name == 'descripcion':
                    entry.insert('1.0', producto[field_name])
                else:
                    entry.insert(0, str(producto[field_name]))
        
        def guardar():
            try:
                producto_data = {}
                for field_name, entry in entries.items():
                    if field_name == 'descripcion':
                        producto_data[field_name] = entry.get('1.0', tk.END).strip()
                    else:
                        producto_data[field_name] = entry.get().strip()
                
                # Validar
                if not producto_data['codigo'] or not producto_data['nombre']:
                    messagebox.showwarning("Advertencia", "Código y Nombre son obligatorios")
                    return
                
                # Convertir números
                producto_data['precio_compra'] = float(producto_data['precio_compra'] or 0)
                producto_data['precio_venta'] = float(producto_data['precio_venta'] or 0)
                producto_data['stock'] = int(producto_data['stock'] or 0)
                producto_data['stock_minimo'] = int(producto_data['stock_minimo'] or 5)
                
                if producto:
                    # Actualizar
                    self.cursor.execute("""
                        UPDATE productos SET
                        codigo=?, nombre=?, descripcion=?, categoria=?,
                        precio_compra=?, precio_venta=?, stock=?,
                        stock_minimo=?, proveedor=?
                        WHERE id=?
                    """, (
                        producto_data['codigo'],
                        producto_data['nombre'],
                        producto_data['descripcion'],
                        producto_data['categoria'],
                        producto_data['precio_compra'],
                        producto_data['precio_venta'],
                        producto_data['stock'],
                        producto_data['stock_minimo'],
                        producto_data['proveedor'],
                        producto['id']
                    ))
                    mensaje = "✅ Producto actualizado"
                else:
                    # Insertar nuevo
                    self.cursor.execute("""
                        INSERT INTO productos
                        (codigo, nombre, descripcion, categoria, precio_compra,
                         precio_venta, stock, stock_minimo, proveedor)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        producto_data['codigo'],
                        producto_data['nombre'],
                        producto_data['descripcion'],
                        producto_data['categoria'],
                        producto_data['precio_compra'],
                        producto_data['precio_venta'],
                        producto_data['stock'],
                        producto_data['stock_minimo'],
                        producto_data['proveedor']
                    ))
                    mensaje = "✅ Producto agregado"
                
                self.conn.commit()
                self.cargar_productos()
                self.actualizar_reportes()
                messagebox.showinfo("Éxito", mensaje)
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Ingrese números válidos en precio y stock")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {e}")
        
        # Botones
        btn_frame = tk.Frame(main_frame, bg=Config.LIGHT_BG)
        btn_frame.grid(row=9, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text="💾 Guardar",
                 command=guardar,
                 bg=Config.SUCCESS_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="✖ Cancelar",
                 command=dialog.destroy,
                 bg=Config.DANGER_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=10)

    # --- MÉTODOS PARA CLIENTES ---

    def cargar_clientes(self):
        """Cargar clientes en el Treeview"""
        for item in self.tree_clientes.get_children():
            self.tree_clientes.delete(item)
        
        try:
            self.cursor.execute("SELECT * FROM clientes ORDER BY nombre")
            clientes = self.cursor.fetchall()
            
            for cliente in clientes:
                self.tree_clientes.insert("", tk.END, values=(
                    cliente['id'],
                    cliente['rut'],
                    cliente['nombre'],
                    cliente['telefono'],
                    cliente['email'],
                    cliente['tipo_cliente']
                ))
            
            self.label_info_clientes.config(text=f"Total clientes: {len(clientes)}")
            
        except Exception as e:
            print(f"Error al cargar clientes: {e}")

    def nuevo_cliente(self):
        """Abrir formulario para nuevo cliente"""
        if not self.tiene_permiso('clientes'):
            messagebox.showwarning("Permiso Denegado", "No tiene permisos para crear clientes")
            return
        
        self.dialogo_cliente(None)

    def editar_cliente(self):
        """Editar cliente seleccionado"""
        if not self.tiene_permiso('clientes'):
            messagebox.showwarning("Permiso Denegado", "No tiene permisos para editar clientes")
            return
        
        selection = self.tree_clientes.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un cliente para editar")
            return
        
        item = self.tree_clientes.item(selection[0])
        cliente_id = item['values'][0]
        
        self.cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
        cliente = self.cursor.fetchone()
        
        if cliente:
            self.dialogo_cliente(cliente)

    def eliminar_cliente(self):
        """Eliminar cliente seleccionado"""
        if not self.tiene_permiso('clientes'):
            messagebox.showwarning("Permiso Denegado", "No tiene permisos para eliminar clientes")
            return
        
        selection = self.tree_clientes.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un cliente para eliminar")
            return
        
        item = self.tree_clientes.item(selection[0])
        cliente_id = item['values'][0]
        cliente_nombre = item['values'][2]
        
        respuesta = messagebox.askyesno("Confirmar",
                                       f"¿Eliminar al cliente: {cliente_nombre}?")
        
        if respuesta:
            try:
                self.cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
                self.conn.commit()
                self.cargar_clientes()
                self.actualizar_reportes()
                messagebox.showinfo("Éxito", "Cliente eliminado")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")

    def dialogo_cliente(self, cliente):
        """Diálogo para agregar/editar cliente"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Nuevo Cliente" if cliente is None else "Editar Cliente")
        dialog.geometry("400x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        main_frame = tk.Frame(dialog, bg=Config.LIGHT_BG, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        campos = [
            ("RUT:", "rut", 0),
            ("Nombre:", "nombre", 1),
            ("Teléfono:", "telefono", 2),
            ("Email:", "email", 3),
            ("Dirección:", "direccion", 4)
        ]
        
        entries = {}
        
        for label_text, field_name, row in campos:
            tk.Label(main_frame, text=label_text, bg=Config.LIGHT_BG).grid(row=row, column=0, sticky=tk.W, pady=5)
            
            if field_name == 'direccion':
                entry = tk.Text(main_frame, height=3, width=30)
                entry.grid(row=row, column=1, pady=5)
            else:
                entry = tk.Entry(main_frame, width=30)
                entry.grid(row=row, column=1, pady=5)
            
            entries[field_name] = entry
        
        if cliente:
            for field_name, entry in entries.items():
                if field_name == 'direccion':
                    entry.insert('1.0', cliente[field_name])
                else:
                    entry.insert(0, str(cliente[field_name]))
        
        # Tipo de cliente
        tk.Label(main_frame, text="Tipo:", bg=Config.LIGHT_BG).grid(row=5, column=0, sticky=tk.W, pady=5)
        tipo_var = tk.StringVar(value=cliente['tipo_cliente'] if cliente else 'normal')
        tipo_combo = ttk.Combobox(main_frame, textvariable=tipo_var,
                                 values=['normal', 'preferencial', 'mayorista'],
                                 width=28, state='readonly')
        tipo_combo.grid(row=5, column=1, pady=5)
        
        def guardar():
            try:
                cliente_data = {}
                for field_name, entry in entries.items():
                    if field_name == 'direccion':
                        cliente_data[field_name] = entry.get('1.0', tk.END).strip()
                    else:
                        cliente_data[field_name] = entry.get().strip()
                
                cliente_data['tipo_cliente'] = tipo_var.get()
                
                if not cliente_data['rut'] or not cliente_data['nombre']:
                    messagebox.showwarning("Advertencia", "RUT y Nombre son obligatorios")
                    return
                
                if cliente:
                    # Actualizar
                    self.cursor.execute("""
                        UPDATE clientes SET
                        rut=?, nombre=?, telefono=?, email=?,
                        direccion=?, tipo_cliente=?
                        WHERE id=?
                    """, (
                        cliente_data['rut'],
                        cliente_data['nombre'],
                        cliente_data['telefono'],
                        cliente_data['email'],
                        cliente_data['direccion'],
                        cliente_data['tipo_cliente'],
                        cliente['id']
                    ))
                    mensaje = "✅ Cliente actualizado"
                else:
                    # Insertar nuevo
                    self.cursor.execute("""
                        INSERT INTO clientes
                        (rut, nombre, telefono, email, direccion, tipo_cliente)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        cliente_data['rut'],
                        cliente_data['nombre'],
                        cliente_data['telefono'],
                        cliente_data['email'],
                        cliente_data['direccion'],
                        cliente_data['tipo_cliente']
                    ))
                    mensaje = "✅ Cliente agregado"
                
                self.conn.commit()
                self.cargar_clientes()
                self.actualizar_reportes()
                messagebox.showinfo("Éxito", mensaje)
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {e}")
        
        # Botones
        btn_frame = tk.Frame(main_frame, bg=Config.LIGHT_BG)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text="💾 Guardar",
                 command=guardar,
                 bg=Config.SUCCESS_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="✖ Cancelar",
                 command=dialog.destroy,
                 bg=Config.DANGER_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=10)

    # --- MÉTODOS PARA VENTAS ---

    def buscar_productos_venta(self, event=None):
        """Buscar productos para venta"""
        search_term = self.search_venta.get()
        
        # Limpiar treeview
        for item in self.tree_productos_venta.get_children():
            self.tree_productos_venta.delete(item)
        
        try:
            if search_term:
                query = "SELECT * FROM productos WHERE (nombre LIKE ? OR codigo LIKE ?) AND stock > 0 ORDER BY nombre"
                params = (f'%{search_term}%', f'%{search_term}%')
            else:
                query = "SELECT * FROM productos WHERE stock > 0 ORDER BY nombre LIMIT 50"
                params = ()
            
            self.cursor.execute(query, params)
            productos = self.cursor.fetchall()
            
            for producto in productos:
                self.tree_productos_venta.insert("", tk.END, values=(
                    producto['id'],
                    producto['nombre'],
                    f"${producto['precio_venta']:,.0f}",
                    producto['stock']
                ))
                
        except Exception as e:
            print(f"Error al buscar productos venta: {e}")

    def agregar_al_carrito(self):
        """Agregar producto seleccionado al carrito"""
        selection = self.tree_productos_venta.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un producto")
            return
        
        item = self.tree_productos_venta.item(selection[0])
        producto_id = item['values'][0]
        producto_nombre = item['values'][1]
        precio = float(item['values'][2].replace('$', '').replace(',', ''))
        stock = item['values'][3]
        
        # Diálogo para cantidad
        dialog = tk.Toplevel(self.root)
        dialog.title("Cantidad")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text=f"Producto: {producto_nombre}").pack(pady=10)
        tk.Label(dialog, text=f"Stock: {stock}").pack()
        
        cantidad_var = tk.StringVar(value="1")
        tk.Entry(dialog, textvariable=cantidad_var, width=10).pack(pady=10)
        
        def agregar():
            try:
                cantidad = int(cantidad_var.get())
                if cantidad <= 0:
                    messagebox.showwarning("Error", "Cantidad debe ser > 0")
                    return
                
                if cantidad > stock:
                    messagebox.showwarning("Error", f"Stock insuficiente. Disponible: {stock}")
                    return
                
                # Agregar al carrito (treeview)
                total = cantidad * precio
                self.tree_carrito.insert("", tk.END, values=(
                    producto_nombre,
                    cantidad,
                    f"${precio:,.0f}",
                    f"${total:,.0f}"
                ))
                
                # Actualizar totales
                self.calcular_totales()
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Ingrese número válido")
        
        tk.Button(dialog, text="Agregar", command=agregar).pack()

    def quitar_del_carrito(self):
        """Quitar producto del carrito"""
        selection = self.tree_carrito.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un producto del carrito")
            return
        
        self.tree_carrito.delete(selection[0])
        self.calcular_totales()

    def vaciar_carrito(self):
        """Vaciar todo el carrito"""
        for item in self.tree_carrito.get_children():
            self.tree_carrito.delete(item)
        self.calcular_totales()

    def calcular_totales(self):
        """Calcular subtotal, IVA y total"""
        subtotal = 0
        
        for item in self.tree_carrito.get_children():
            item_data = self.tree_carrito.item(item)
            total_str = item_data['values'][3]
            total = float(total_str.replace('$', '').replace(',', ''))
            subtotal += total
        
        iva = subtotal * Config.IVA_PORCENTAJE
        total = subtotal + iva
        
        self.label_subtotal.config(text=f"${subtotal:,.0f}")
        self.label_iva.config(text=f"${iva:,.0f}")
        self.label_total.config(text=f"${total:,.0f}")

    def finalizar_venta(self):
        """Finalizar la venta actual"""
        if not self.tiene_permiso('ventas'):
            messagebox.showwarning("Permiso Denegado", "No tiene permisos para realizar ventas")
            return
        
        if not self.tree_carrito.get_children():
            messagebox.showwarning("Advertencia", "Carrito vacío")
            return
        
        # Obtener total
        total = float(self.label_total.cget('text').replace('$', '').replace(',', ''))
        
        # Diálogo simple para confirmar
        respuesta = messagebox.askyesno("Confirmar Venta",
                                       f"¿Confirmar venta por ${total:,.0f}?")
        
        if respuesta:
            try:
                # Generar folio
                fecha = datetime.now().strftime("%Y%m%d")
                self.cursor.execute("SELECT COUNT(*) FROM ventas WHERE DATE(fecha_venta) = DATE('now')")
                numero = self.cursor.fetchone()[0] + 1
                folio = f"VTA-{fecha}-{numero:04d}"
                
                # Calcular subtotal e IVA
                subtotal = float(self.label_subtotal.cget('text').replace('$', '').replace(',', ''))
                iva = float(self.label_iva.cget('text').replace('$', '').replace(',', ''))
                
                # Insertar venta (agregar usuario_id)
                self.cursor.execute("""
                    INSERT INTO ventas (numero_folio, usuario_id, subtotal, iva, total, metodo_pago)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (folio, self.usuario['id'], subtotal, iva, total, 'efectivo'))
                
                venta_id = self.cursor.lastrowid
                
                # Insertar detalles y actualizar stock
                for item in self.tree_carrito.get_children():
                    item_data = self.tree_carrito.item(item)
                    producto_nombre = item_data['values'][0]
                    cantidad = item_data['values'][1]
                    precio = float(item_data['values'][2].replace('$', '').replace(',', ''))
                    
                    # Obtener ID del producto
                    self.cursor.execute("SELECT id FROM productos WHERE nombre = ?", (producto_nombre,))
                    producto = self.cursor.fetchone()
                    
                    if producto:
                        # Insertar detalle
                        self.cursor.execute("""
                            INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario, total_linea)
                            VALUES (?, ?, ?, ?, ?)
                        """, (venta_id, producto['id'], cantidad, precio, cantidad * precio))
                        
                        # Actualizar stock
                        self.cursor.execute("""
                            UPDATE productos SET stock = stock - ? WHERE id = ?
                        """, (cantidad, producto['id']))
                
                self.conn.commit()
                
                messagebox.showinfo("Éxito",
                                   f"Venta realizada\nFolio: {folio}\nTotal: ${total:,.0f}")
                
                # Limpiar y actualizar
                self.vaciar_carrito()
                self.buscar_productos_venta()
                self.cargar_productos()
                self.actualizar_reportes()
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo procesar la venta: {e}")

    # --- MÉTODOS PARA REPORTES ---

    def actualizar_reportes(self):
        """Actualizar todos los reportes"""
        try:
            # Total productos
            self.cursor.execute("SELECT COUNT(*) FROM productos")
            total_p = self.cursor.fetchone()[0]
            self.label_total_productos.config(text=f"Total Productos: {total_p}")
            
            # Productos con stock bajo
            self.cursor.execute("SELECT COUNT(*) FROM productos WHERE stock <= stock_minimo")
            bajo = self.cursor.fetchone()[0]
            self.label_productos_bajo.config(text=f"Productos con Stock Bajo: {bajo}")
            
            # Total clientes
            self.cursor.execute("SELECT COUNT(*) FROM clientes")
            total_c = self.cursor.fetchone()[0]
            self.label_total_clientes.config(text=f"Total Clientes: {total_c}")
            
            # Ventas hoy
            self.cursor.execute("SELECT COUNT(*) FROM ventas WHERE DATE(fecha_venta) = DATE('now')")
            ventas_hoy = self.cursor.fetchone()[0]
            self.label_ventas_hoy.config(text=f"Ventas Hoy: {ventas_hoy}")
            
            # Actualizar barra de estado
            self.status_bar.config(text=f"Don Willy Ferretería | Productos: {total_p} | Clientes: {total_c} | Ventas hoy: {ventas_hoy}")
            
        except Exception as e:
            print(f"Error al actualizar reportes: {e}")

    # --- MÉTODOS PARA USUARIOS ---
    
    def cargar_usuarios(self):
        """Cargar usuarios en el Treeview"""
        for item in self.tree_usuarios.get_children():
            self.tree_usuarios.delete(item)
        
        try:
            self.cursor.execute("SELECT * FROM usuarios ORDER BY username")
            usuarios = self.cursor.fetchall()
            
            for usuario in usuarios:
                activo = "✅" if usuario['activo'] else "❌"
                ultimo_login = usuario['ultimo_login'] if usuario['ultimo_login'] else "Nunca"
                
                self.tree_usuarios.insert("", tk.END, values=(
                    usuario['id'],
                    usuario['username'],
                    usuario['nombre_completo'],
                    usuario['email'],
                    Config.ROLES.get(usuario['rol'], usuario['rol']),
                    activo,
                    ultimo_login
                ))
            
            self.label_info_usuarios.config(text=f"Total usuarios: {len(usuarios)}")
            
        except Exception as e:
            print(f"Error al cargar usuarios: {e}")
            messagebox.showerror("Error", f"No se pudieron cargar los usuarios: {e}")
    
    def nuevo_usuario(self):
        """Abrir formulario para nuevo usuario"""
        self.dialogo_usuario(None)
    
    def editar_usuario(self):
        """Editar usuario seleccionado"""
        selection = self.tree_usuarios.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un usuario para editar")
            return
        
        item = self.tree_usuarios.item(selection[0])
        usuario_id = item['values'][0]
        
        self.cursor.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,))
        usuario = self.cursor.fetchone()
        
        if usuario:
            self.dialogo_usuario(usuario)
    
    def eliminar_usuario(self):
        """Eliminar usuario seleccionado"""
        selection = self.tree_usuarios.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Seleccione un usuario para eliminar")
            return
        
        item = self.tree_usuarios.item(selection[0])
        usuario_id = item['values'][0]
        username = item['values'][1]
        
        if username == self.usuario['username']:
            messagebox.showwarning("Advertencia", "No puede eliminar su propio usuario")
            return
        
        respuesta = messagebox.askyesno("Confirmar",
                                       f"¿Eliminar al usuario: {username}?")
        
        if respuesta:
            try:
                self.cursor.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))
                self.conn.commit()
                self.cargar_usuarios()
                messagebox.showinfo("Éxito", "Usuario eliminado correctamente")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")
    
    def dialogo_usuario(self, usuario):
        """Diálogo para agregar/editar usuario"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Nuevo Usuario" if usuario is None else "Editar Usuario")
        dialog.geometry("500x550")
        dialog.transient(self.root)
        dialog.grab_set()
        
        main_frame = tk.Frame(dialog, bg=Config.LIGHT_BG, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        campos = [
            ("Username:", "username", 0),
            ("Nombre Completo:", "nombre_completo", 1),
            ("Email:", "email", 2),
            ("Contraseña:", "password", 3),
            ("Confirmar Contraseña:", "password2", 4)
        ]
        
        entries = {}
        
        for label_text, field_name, row in campos:
            tk.Label(main_frame, text=label_text, bg=Config.LIGHT_BG).grid(row=row, column=0, sticky=tk.W, pady=5)
            
            if 'password' in field_name:
                entry = tk.Entry(main_frame, width=40, show="*")
            else:
                entry = tk.Entry(main_frame, width=40)
            
            entry.grid(row=row, column=1, pady=5)
            entries[field_name] = entry
        
        # Rol
        tk.Label(main_frame, text="Rol:", bg=Config.LIGHT_BG).grid(row=5, column=0, sticky=tk.W, pady=5)
        rol_var = tk.StringVar(value=usuario['rol'] if usuario else 'cajero')
        rol_combo = ttk.Combobox(main_frame, textvariable=rol_var,
                                values=list(Config.ROLES.keys()),
                                width=37, state='readonly')
        rol_combo.grid(row=5, column=1, pady=5)
        
        # Activo
        tk.Label(main_frame, text="Activo:", bg=Config.LIGHT_BG).grid(row=6, column=0, sticky=tk.W, pady=5)
        activo_var = tk.BooleanVar(value=usuario['activo'] if usuario else True)
        tk.Checkbutton(main_frame, variable=activo_var, bg=Config.LIGHT_BG).grid(row=6, column=1, sticky=tk.W, pady=5)
        
        # Si hay datos, llenar campos (excepto contraseñas)
        if usuario:
            entries['username'].insert(0, usuario['username'])
            entries['nombre_completo'].insert(0, usuario['nombre_completo'])
            entries['email'].insert(0, usuario['email'] if usuario['email'] else "")
            entries['username'].config(state='readonly' if usuario['username'] == 'admin' else 'normal')
        
        def guardar():
            try:
                usuario_data = {}
                for field_name, entry in entries.items():
                    usuario_data[field_name] = entry.get().strip()
                
                usuario_data['rol'] = rol_var.get()
                usuario_data['activo'] = activo_var.get()
                
                # Validaciones
                if not usuario_data['username'] or not usuario_data['nombre_completo']:
                    messagebox.showwarning("Advertencia", "Username y Nombre son obligatorios")
                    return
                
                if not usuario and (not usuario_data['password'] or not usuario_data['password2']):
                    messagebox.showwarning("Advertencia", "La contraseña es obligatoria para nuevos usuarios")
                    return
                
                if usuario_data['password'] != usuario_data['password2']:
                    messagebox.showwarning("Advertencia", "Las contraseñas no coinciden")
                    return
                
                # Insertar o actualizar
                if usuario:
                    # Actualizar usuario
                    if usuario_data['password']:
                        # Actualizar con nueva contraseña
                        salt = secrets.token_hex(16)
                        password_hash = hashlib.sha256((usuario_data['password'] + salt).encode()).hexdigest()
                        
                        self.cursor.execute("""
                            UPDATE usuarios SET
                            nombre_completo=?, email=?, rol=?, activo=?,
                            password_hash=?, salt=?
                            WHERE id=?
                        """, (
                            usuario_data['nombre_completo'],
                            usuario_data['email'],
                            usuario_data['rol'],
                            1 if usuario_data['activo'] else 0,
                            password_hash,
                            salt,
                            usuario['id']
                        ))
                    else:
                        # Actualizar sin cambiar contraseña
                        self.cursor.execute("""
                            UPDATE usuarios SET
                            nombre_completo=?, email=?, rol=?, activo=?
                            WHERE id=?
                        """, (
                            usuario_data['nombre_completo'],
                            usuario_data['email'],
                            usuario_data['rol'],
                            1 if usuario_data['activo'] else 0,
                            usuario['id']
                        ))
                    
                    mensaje = "✅ Usuario actualizado"
                else:
                    # Insertar nuevo usuario
                    salt = secrets.token_hex(16)
                    password_hash = hashlib.sha256((usuario_data['password'] + salt).encode()).hexdigest()
                    
                    self.cursor.execute("""
                        INSERT INTO usuarios
                        (username, password_hash, nombre_completo, email, rol, activo, salt)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        usuario_data['username'],
                        password_hash,
                        usuario_data['nombre_completo'],
                        usuario_data['email'],
                        usuario_data['rol'],
                        1 if usuario_data['activo'] else 0,
                        salt
                    ))
                    
                    mensaje = "✅ Usuario agregado"
                
                self.conn.commit()
                self.cargar_usuarios()
                messagebox.showinfo("Éxito", mensaje)
                dialog.destroy()
                
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "El username ya existe")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {e}")
        
        # Botones
        btn_frame = tk.Frame(main_frame, bg=Config.LIGHT_BG)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        tk.Button(btn_frame, text="💾 Guardar",
                 command=guardar,
                 bg=Config.SUCCESS_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_frame, text="✖ Cancelar",
                 command=dialog.destroy,
                 bg=Config.DANGER_COLOR,
                 fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=10)

def crear_tablas_iniciales():
    """Crear tablas iniciales si no existen"""
    print("🔧 Verificando base de datos...")
    conn = sqlite3.connect(Config.SQLITE_DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Tabla usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                nombre_completo VARCHAR(100) NOT NULL,
                email VARCHAR(100),
                rol VARCHAR(20) DEFAULT 'cajero',
                activo BOOLEAN DEFAULT 1,
                fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
                ultimo_login DATETIME,
                salt VARCHAR(50) NOT NULL
            )
        """)
        
        # Tabla productos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo VARCHAR(50) UNIQUE NOT NULL,
                nombre VARCHAR(100) NOT NULL,
                descripcion TEXT,
                categoria VARCHAR(50),
                precio_compra DECIMAL(10,2) NOT NULL,
                precio_venta DECIMAL(10,2) NOT NULL,
                stock INTEGER DEFAULT 0,
                stock_minimo INTEGER DEFAULT 5,
                proveedor VARCHAR(100),
                fecha_ingreso DATE DEFAULT CURRENT_DATE
            )
        """)
        
        # Tabla clientes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rut VARCHAR(20) UNIQUE NOT NULL,
                nombre VARCHAR(100) NOT NULL,
                telefono VARCHAR(20),
                email VARCHAR(100),
                direccion TEXT,
                tipo_cliente VARCHAR(20) DEFAULT 'normal',
                fecha_registro DATE DEFAULT CURRENT_DATE
            )
        """)
        
        # Tabla ventas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_folio VARCHAR(50) UNIQUE NOT NULL,
                cliente_id INTEGER,
                usuario_id INTEGER,
                fecha_venta DATETIME DEFAULT CURRENT_TIMESTAMP,
                subtotal DECIMAL(10,2) NOT NULL,
                iva DECIMAL(10,2) NOT NULL,
                total DECIMAL(10,2) NOT NULL,
                metodo_pago VARCHAR(20),
                estado VARCHAR(20) DEFAULT 'completada',
                FOREIGN KEY (cliente_id) REFERENCES clientes(id)
            )
        """)
        
        # Tabla detalle_ventas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detalle_ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER NOT NULL,
                producto_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario DECIMAL(10,2) NOT NULL,
                total_linea DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (venta_id) REFERENCES ventas(id),
                FOREIGN KEY (producto_id) REFERENCES productos(id)
            )
        """)
        
        # Insertar usuario admin por defecto si no existe
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE username = 'admin'")
        if cursor.fetchone()[0] == 0:
            salt = secrets.token_hex(16)
            password_hash = hashlib.sha256(('admin123' + salt).encode()).hexdigest()
            cursor.execute("""
                INSERT INTO usuarios (username, password_hash, nombre_completo, email, rol, salt)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ('admin', password_hash, 'Administrador Principal', 'admin@donwilly.cl', 'admin', salt))
            print("✅ Usuario admin creado: admin / admin123")
        
        conn.commit()
        print("✅ Base de datos verificada correctamente")
        
    except Exception as e:
        print(f"❌ Error al crear tablas: {e}")
        conn.rollback()
    finally:
        conn.close()

def main():
    """Función principal"""
    print("=" * 50)
    print("  FERRETERÍA DON WILLY")
    print("  Sistema de Gestión")
    print("=" * 50)
    
    # Crear tablas si no existen
    crear_tablas_iniciales()
    
    # Mostrar ventana de login
    login_window = LoginWindow()
    usuario = login_window.run()
    
    if not usuario:
        print("❌ Login cancelado o fallido")
        return
    
    print(f"✅ Usuario autenticado: {usuario['nombre_completo']} ({usuario['rol']})")
    
    # Crear ventana principal
    root = tk.Tk()
    app = SistemaFerreteriaGUI(root, usuario)
    
    # Centrar ventana
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()