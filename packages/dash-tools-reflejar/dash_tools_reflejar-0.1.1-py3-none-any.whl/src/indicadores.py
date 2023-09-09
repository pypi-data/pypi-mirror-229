import textwrap
import locale

import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

from dash import dash, html, dcc, Input, Output, State, callback
from dash_loading_spinners import Hash
from ._chart_types import histogram as reflejar_histogram
# Esto habría que corregir para hacer una libreria publicable


# COLORES
ROJO = '--bs-red'
VERDE_AGUA= '--bs-teal'
CELESTE = '--bs-cyan'
LILA = '--bs-purple'
NARANJA= '--bs-orange'
LIMA= '--bs-yellow'
NEGRO =  '--bs-black'

# Establecer la configuración regional según tu preferencia (por ejemplo, en_US para inglés en Estados Unidos)
locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')

class Indicador:
    """
        Clase para crear los diferentes indicadores
    """

    LETRA_DEFAULT = "Arial"
    LETRA_COLOR = 'black'
    TAMANIO_FUENTE = 16

    def __init__(
        self,
        df, 
        id_indicador="", 
        colores=[], 
        tipo_grafico="bar",
        titulo_grafico="" ,
        y="", 
        y_titulo="",
        x="",
        x_titulo="",
        z="",
        hover="",
        porcentaje=False,
        texto_descriptivo = '',
        divisor = 1

    ) -> None:
        self.id = id_indicador
        self.df = df.copy()
        self.colores = colores
        self.tipo_grafico = tipo_grafico
        self.titulo_grafico = titulo_grafico
        self.y_var = y
        self.y_titulo = y_titulo or y
        self.x_var = x
        self.x_titulo = x_titulo or x
        self.z_var = z
        self.hover = hover
        self.porcentaje = porcentaje
        self.texto_descriptivo = texto_descriptivo
        self.divisor = divisor

    def inicializar(self):
        """
            Esto es para la carga inicial. Lo que va fuera del callback
        """
        return html.Div([
            dbc.Card(
                [
                    dbc.CardBody(
                        Hash(dbc.Row(
                            [
                            dbc.Col(dcc.Graph(id=self.id), md=12),                
                            ]
                        ),
                        size=24,
                        color=self.colores[0],
                        )
                        
                    ),
                    dbc.CardFooter(
                        dbc.Button("Ver más", 
                                    id=f"modal-open-{self.id}", 
                                    style={
                                        "background-color": NEGRO, 
                                        "border-color": "#FFFFFF", 
                                        "color": "#FFFFFF", 
                                        "font-family": self.LETRA_DEFAULT
                                        }
                                    ), 
                                    className="text-center", 
                                    style={"background-color": "light","border": "none", "color": "light"}),
                    
                ],
                color="light", 
                class_name="shadow mb-5",    
                outline=True,
                id=f"tarjeta-{self.id}"
            ),
            dbc.Modal(
                    [
                        dbc.ModalHeader(html.H4(html.Strong(self.titulo_grafico), style = {"font-family": self.LETRA_DEFAULT}, className="text-dark text-center"), ),
                        dbc.ModalBody([
                            dbc.Row(dbc.Col(html.P(self.texto_descriptivo,className="text-dark" ))),
                            dcc.Graph(id=f"modal-graph-{self.id}")                            
                    ]),
                        dbc.ModalFooter(
                            dbc.Button("Volver atrás", 
                                        id=f"modal-close-{self.id}", 
                                        color="light",style={"background-color": NEGRO, "border-color": "#FFFFFF", "color": "#FFFFFF", "font-family": self.LETRA_DEFAULT},  
                                        className="mx-auto"), className="text-center", 
                                        style={
                                            "background-color": "#FFFFFF" ,
                                            "border": "none", 
                                            "color": "none"}
                        ),
                    ],
                    id=f"modal-{self.id}",
                    size="lg",
                    is_open=False,
                )
        ])

    def bar(self, df):
        return px.bar(
            df, 
            x=self.x_var, 
            y=self.y_var, 
            color_discrete_sequence=[self.colores[0]], 
            text='y_text'
        )

    def histogram(self, df):
        return reflejar_histogram(
            df, 
            x=self.x_var, 
            y=self.y_var, 
            color=self.z_var, 
            # color='Tamaño EAPs',
            barnorm='percent' if self.porcentaje else None,  
            color_discrete_sequence=self.colores,
            text='y_text',         
        )
        
    def area(self, df):
        return px.area(
            df, 
            x=self.x_var, 
            y=self.y_var, 
            color=self.z_var or None,  
            color_discrete_sequence=self.colores,
        )

    def pie(self, df):
        return px.pie(
            df, 
            values=self.y_var, 
            names=self.x_var, 
            color_discrete_sequence=self.colores
        )
    
    def number(self, df):
        _valor = df[self.y_var].values
        _valor = _valor[0]
        return go.Figure(go.Indicator(
            mode = "number",
            value = _valor,
            ))
    
    def actualizar(self, partido):
        """
            Esto va para el callback
        """
        df = self.df.copy()
        # Limpieza de datos
        if VAR_ANIO_CENSO in df.columns:
            df[VAR_ANIO_CENSO] = df[VAR_ANIO_CENSO].astype(int).astype(str)

        if VAR_EAPS_Q in df.columns:
            df[VAR_EAPS_Q]= round(df[VAR_EAPS_Q],2)
        
        # Captura del filtro
        
        if partido:
            mask = df[VAR_PARTIDO]==partido
            df = df[mask]
        
        if self.tipo_grafico != 'number':
            grupos = [self.x_var, VAR_PARTIDO]
            if self.z_var:
                grupos.append(self.z_var)

            df = df.groupby(by = grupos)[self.y_var].sum().reset_index()
            df[self.y_var] = (df[self.y_var]/self.divisor).astype(int)
            df['y_text'] = df[self.y_var].apply(lambda x: f'{x:,}'.replace(',', '.'))        

            fig = getattr(self, self.tipo_grafico)(df)
            fig.update_xaxes( title_text = self.x_titulo, title_font=dict(size=self.TAMANIO_FUENTE, family=self.LETRA_DEFAULT, color=self.LETRA_COLOR), tickfont=dict(family=self.LETRA_DEFAULT, color=self.LETRA_COLOR, size=11))
            fig.update_yaxes(title_text = self.y_titulo,  title_font=dict(size=self.TAMANIO_FUENTE,family=self.LETRA_DEFAULT,color=self.LETRA_COLOR), tickfont=dict(family=self.LETRA_DEFAULT, color=self.LETRA_COLOR, size=11))
            fig.update_layout(yaxis=dict(tickformat='.0f',ticksuffix='')) #se le saca la K a los números del eje de las y


            #Armar el texto de las etiquetas emergentes
            fig.update_traces(hovertemplate=self.hover)

        else:            
            fig = getattr(self, self.tipo_grafico)(df)
            fig.update_layout(font = {'color': self.colores[0], 'family': self.LETRA_DEFAULT})
        
        
        # Actualizar el diseño del gráfico
        fig.update_layout(
            title={
            "text": f"<b>{'<br>'.join(textwrap.wrap(self.titulo_grafico, width=30))}</b>",
            "x": 0.5,
            "y": 0.95,
            "xanchor": "center",
            "yanchor": "top",
            "font": {
                "size": 17,
                "color": "black",
                "family": self.LETRA_DEFAULT
            },
            "yref": "container",
            "yanchor": "top"
            },
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis_tickangle=-45,
            hovermode="x",
            legend=dict(
                title='',
                orientation="h",
                xanchor='center',
                x=0.5,
                y=-0.3,
                bgcolor='rgba(255, 255, 255, 0)',
                bordercolor='rgba(255, 255, 255, 0)',
                tracegroupgap=10
            )
        )
        
        return fig
    
    @staticmethod
    def generar_callbacks(indicadores):
        for i in range(len(indicadores)):
            id_indicador = indicadores[i].id
            @callback(
                Output(id_indicador, "figure"),
                Input("select-partido", "value"),
            )
            def update_graph(selected_value, i=i):
                return indicadores[i].actualizar(selected_value)
            
            @callback(
                [
                    Output(f"modal-{id_indicador}", "is_open"),
                    Output(f"modal-graph-{id_indicador}", "figure"),
                    Output(f"modal-open-{id_indicador}", "n_clicks"),
                ],
                [
                    Input(f"modal-open-{id_indicador}", 'n_clicks'),
                    Input(f"modal-close-{id_indicador}", "n_clicks"),
                ],
                [
                    State(f"modal-{id_indicador}", "is_open"),
                    State(f"{id_indicador}", "figure")
                ]
            )
            def toggle_modal(open_modal, close_modal, is_open_modal, figure, i=i):
                if is_open_modal:
                    return False, dash.no_update, 0
                if open_modal:
                    return True, figure, 1
                return is_open_modal, dash.no_update,0
