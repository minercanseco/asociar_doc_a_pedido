import datetime
import tkinter as tk
from cayal.ventanas import Ventanas
from cayal.util import Utilerias
from cayal.comandos_base_datos import ComandosBaseDatos


class AsociarAPedido:
    def __init__(self, master, parametros):
        self._master = master
        self._parametros = parametros
        self._ventanas = Ventanas(self._master)
        self._utilerias = Utilerias()
        self._base_de_datos = ComandosBaseDatos()

        self._document_id = self._parametros.id_principal
        self._module_id = self._parametros.id_modulo
        self._hoy = '2025-11-18' #str(datetime.datetime.today().date())

        self._info_documento = self._buscar_info_documento(self._document_id)

        self._crear_frames()
        self._cargar_componentes()
        self._cargar_eventos()
        self._rellenar_componentes()

        self._ventanas.configurar_ventana_ttkbootstrap(titulo='Asociar documento', master=self._master)

    def _buscar_info_documento(self, document_id):
        consulta = self._base_de_datos.buscar_info_documento(document_id)
        if consulta:
            info_documento = consulta[0]
            return info_documento

        return {}

    def _crear_frames(self):
        frames = {
            'frame_principal': ('master', None,
                                {'row': 0, 'column': 0, 'sticky': tk.W}),

            'frame_componentes': ('frame_principal', 'Generales:',
                                  {'row': 2, 'column': 0, 'padx': 5, 'pady': 5, 'sticky': tk.W}),

            'frame_tabla1': ('frame_componentes', 'Pedidos:',
                              {'row': 4, 'column': 0, 'columnspan':2,  'padx': 5, 'pady': 5, 'sticky': tk.NSEW}),

            'frame_tabla2': ('frame_componentes', 'Documentos:',
                            {'row': 5, 'column': 0,'columnspan':2,  'padx': 5, 'pady': 5, 'sticky': tk.NSEW}),

            'frame_botones': ('frame_componentes', None,
                                  {'row': 6, 'column': 1,  'sticky': tk.NSEW}),

        }

        self._ventanas.crear_frames(frames)

    def _cargar_componentes(self):
        componentes = {
            'tbx_cliente': ('frame_componentes', None, 'Cliente:', None),
            'tbx_folio': ('frame_componentes', None, 'Folio:', None),
            'tbx_capturado': ('frame_componentes', None, 'Capturó:', None),
            'txt_comentario': ('frame_componentes', None, 'Coms:', None),
            'btn_asociar': ('frame_botones', None, 'Asociar', None),
            'btn_cancelar': ('frame_botones', 'Danger', 'Cancelar', None),
            'tvw_tabla1': ('frame_tabla1', self._columnas_tabla(), 5, 'Primary'),
            'tvw_tabla2': ('frame_tabla2', self._columnas_tabla_doctos(), 5, 'Warning'),
        }

        self._ventanas.crear_componentes(componentes)

    def _cargar_eventos(self):
        eventos = {
            'btn_cancelar': self._master.destroy,
            'btn_asociar': self._asociar_documento,
            'tvw_tabla1':(lambda event:self._actualizar_comentario(), 'seleccion'),

        }
        self._ventanas.cargar_eventos(eventos)
        evento_adicional ={
            'tvw_tabla1': (lambda event: self._rellenar_tabla_documentos(), 'seleccion')
        }
        self._ventanas.cargar_eventos(evento_adicional)

    def _rellenar_componentes(self):
        user_created_by = self._base_de_datos.buscar_nombre_de_usuario(self._info_documento['CreatedBy'])
        official_name = self._info_documento['OfficialName']
        official_name = self._utilerias.limitar_caracteres(official_name, 20)

        self._ventanas.insertar_input_componente('tbx_cliente', official_name)
        self._ventanas.insertar_input_componente('tbx_folio', self._info_documento['DocFolio'])
        self._ventanas.insertar_input_componente('tbx_capturado', user_created_by)
        self._ventanas.insertar_input_componente('txt_comentario', self._info_documento['Comments'])

        self._ventanas.bloquear_componente('tbx_cliente')
        self._ventanas.bloquear_componente('tbx_folio')
        self._ventanas.bloquear_componente('tbx_capturado')
        self._ventanas.bloquear_componente('txt_comentario')

        self._ventanas.ajustar_ancho_componente('tbx_cliente', 20)

        self._ventanas.rellenar_treeview('tvw_tabla1',
                                         self._columnas_tabla(),
                                         self._buscar_pedidos_asociados(),
                                         5
                                         )

    def _columnas_tabla(self):
        return [
            {"text": "Folio", "stretch": False, 'width': 100, 'column_anchor': tk.W, 'heading_anchor': tk.W,
             'hide': 0},
            {"text": "Total", "stretch": False, 'width': 90, 'column_anchor': tk.W, 'heading_anchor': tk.W,
             'hide': 0},
            {"text": "Capturó", "stretch": False, 'width': 90, 'column_anchor': tk.W, 'heading_anchor': tk.W,
             'hide': 0},
            {"text": "Entrega", "stretch": False, 'width': 60, 'column_anchor': tk.W, 'heading_anchor': tk.W,
             'hide': 0},
            {"text": "Dirección", "stretch": False, 'width': 150, 'column_anchor': tk.W, 'heading_anchor': tk.W,
             'hide': 0},
            {"text": "CommentsOrder", "stretch": False, 'width': 90, 'column_anchor': tk.W, 'heading_anchor': tk.W,
             'hide': 1},
            {"text": "OrderDocumentID", "stretch": False, 'width': 90, 'column_anchor': tk.W, 'heading_anchor': tk.W,
             'hide': 1},
        ]

    def _columnas_tabla_doctos(self):
        return [
            {"text": "DocumentID", "stretch": False, 'width': 90, 'column_anchor': tk.W, 'heading_anchor': tk.W,
             'hide': 1},
            {"text": "Folio", "stretch": False, 'width': 100, 'column_anchor': tk.W, 'heading_anchor': tk.W,
             'hide': 0},
            {"text": "Total", "stretch": False, 'width': 90, 'column_anchor': tk.W, 'heading_anchor': tk.W,
             'hide': 0},
            {"text": "Capturó", "stretch": False, 'width': 90, 'column_anchor': tk.W, 'heading_anchor': tk.W,
             'hide': 0}

        ]

    def _rellenar_tabla_documentos(self):
        if not self._ventanas.validar_seleccion_una_fila_treeview('tvw_tabla1'):
            return

        filas = self._ventanas.obtener_seleccion_filas_treeview('tvw_tabla1')

        for fila in filas:
            valores = self._ventanas.procesar_fila_treeview('tvw_tabla1', fila)
            order_document_id = valores['OrderDocumentID']
            consulta = self._buscar_documentos_asociados(order_document_id)
            self._ventanas.rellenar_treeview('tvw_tabla2', self._columnas_tabla_doctos(), consulta, 5)

    def _buscar_pedidos_asociados(self):
        return self._base_de_datos.fetchall("""
            SELECT
                ISNULL(P.FolioPrefix,'')+ISNULL(P.Folio,'') Folio,
                CAST(ISNULL(Total, 0) AS DECIMAL(18,2)) AS Total,
                U.UserName Captura,
                SC.Value,
                AD.AddressName, 
                P.CommentsOrder,
                P.OrderDocumentID
            FROM docDocumentOrderCayal P
                INNER JOIN engUser U ON P.CreatedBy = U.UserID
                INNER JOIN OrderSchedulesCayal SC ON P.ScheduleID = SC.ScheduleID
                INNER JOIN orgAddress AD ON P.AddressDetailID = AD.AddressDetailID
            WHERE
                CAST(P.DeliveryPromise as date) = CAST(? as date)
                AND P.BusinessEntityID = ? 
        """, (self._hoy, self._info_documento['BusinessEntityID']))

    def _buscar_documentos_asociados(self, order_document_id):
        return self._base_de_datos.fetchall("""
            SELECT D.DocumentID, ISNULL(D.FolioPrefix, '')+ISNULL(D.Folio, '') DofFolio,
                CAST(ISNULL(D.Total, 0) AS DECIMAL(18,2)) AS Total,
                U.UserName
            FROM 
                docDocument D
                INNER JOIN OrderInvoiceDocumentCayal DI ON D.OrderDocumentID = DI.OrderDocumentID
                INNER JOIN engUser U ON D.CreatedBy = U.UserID
            WHERE
                DI.OrderDocumentID = ? 
                AND D.CancelledOn IS NULL
            ORDER BY DocumentID DESC
        """,(order_document_id,))

    def _actualizar_comentario(self):
        if not self._ventanas.validar_seleccion_una_fila_treeview('tvw_tabla1'):
            return

        filas = self._ventanas.obtener_seleccion_filas_treeview('tvw_tabla1')

        for fila in filas:
            valores = self._ventanas.procesar_fila_treeview('tvw_tabla1', fila)
            comentarios = valores['CommentsOrder']
            self._ventanas.insertar_input_componente('txt_comentario', comentarios)

    def _asociar_documento(self):
        # comprobar relacion de pedidos
        # agregar documento
        pass