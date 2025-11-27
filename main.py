import ttkbootstrap as ttk
from asociar_a_pedido import AsociarAPedido
from cayal.parametros_contpaqi import ParametrosContpaqi


if __name__ == '__main__':
    ventana = ttk.Window()

    parametros = ParametrosContpaqi()
    parametros.id_usuario = 64
    parametros.id_principal = 285387
    parametros.id_modulo = 21

    _= AsociarAPedido(ventana, parametros)
    ventana.mainloop()