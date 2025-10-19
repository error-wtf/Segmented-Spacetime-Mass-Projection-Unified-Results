"""
3D visualization module using Plotly.
Creates interactive segmented spacetime mesh visualizations with UI controls.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union
import dash
from dash import dcc, html, Input, Output, callback
import json

def create_mesh_trace(vertices: np.ndarray, faces: np.ndarray, 
                     scalars: np.ndarray, colorscale: str = "Turbo",
                     opacity: float = 0.35, name: str = "Mesh") -> go.Mesh3d:
    """
    Create 3D mesh trace for Plotly.
    
    Parameters:
    -----------
    vertices : np.ndarray, shape (N, 3)
        Mesh vertex positions
    faces : np.ndarray, shape (M, 3)
        Triangle face indices
    scalars : np.ndarray, shape (N,)
        Scalar field values at vertices
    colorscale : str
        Plotly colorscale name
    opacity : float
        Mesh opacity
    name : str
        Trace name
        
    Returns:
    --------
    mesh_trace : go.Mesh3d
        Plotly mesh trace
    """
    
    i, j, k = faces.T
    
    mesh_trace = go.Mesh3d(
        x=vertices[:, 0],
        y=vertices[:, 1], 
        z=vertices[:, 2],
        i=i, j=j, k=k,
        intensity=scalars,
        colorscale=colorscale,
        opacity=opacity,
        lighting=dict(
            ambient=0.6,
            diffuse=0.8,
            specular=0.2,
            roughness=0.1,
            fresnel=0.2
        ),
        lightposition=dict(x=100, y=100, z=100),
        showscale=True,
        colorbar=dict(
            title=dict(text=name, side="right"),
            tickmode="linear",
            tick0=scalars.min(),
            dtick=(scalars.max() - scalars.min()) / 10
        ),
        name=name,
        hovertemplate=f"<b>{name}</b><br>" +
                     "x: %{x:.2f} AU<br>" +
                     "y: %{y:.2f} AU<br>" +
                     "z: %{z:.2f} AU<br>" +
                     f"{name}: %{{intensity:.3f}}<br>" +
                     "<extra></extra>"
    )
    
    return mesh_trace

def create_body_trace(positions: np.ndarray, names: List[str], 
                     masses: np.ndarray, radii: np.ndarray,
                     colors: Optional[List[str]] = None) -> go.Scatter3d:
    """
    Create celestial body scatter trace.
    
    Parameters:
    -----------
    positions : np.ndarray, shape (N, 3)
        Body positions in AU
    names : list
        Body names
    masses : np.ndarray
        Body masses in kg
    radii : np.ndarray
        Body radii in km
    colors : list, optional
        Body colors
        
    Returns:
    --------
    body_trace : go.Scatter3d
        Plotly scatter trace for bodies
    """
    
    if colors is None:
        colors = ['yellow'] * len(names)
    
    # Scale marker sizes based on radius (log scale)
    marker_sizes = np.log10(radii + 1) * 5 + 5
    marker_sizes = np.clip(marker_sizes, 5, 50)
    
    body_trace = go.Scatter3d(
        x=positions[:, 0],
        y=positions[:, 1],
        z=positions[:, 2],
        mode='markers+text',
        marker=dict(
            size=marker_sizes,
            color=colors,
            opacity=0.8,
            line=dict(width=2, color='white')
        ),
        text=names,
        textposition="top center",
        textfont=dict(size=10, color='white'),
        name="Bodies",
        hovertemplate="<b>%{text}</b><br>" +
                     "Position: (%{x:.2f}, %{y:.2f}, %{z:.2f}) AU<br>" +
                     "Mass: %{customdata[0]:.2e} kg<br>" +
                     "Radius: %{customdata[1]:.0f} km<br>" +
                     "<extra></extra>",
        customdata=np.column_stack([masses, radii])
    )
    
    return body_trace

def create_orbit_traces(orbit_visualizer) -> List[go.Scatter3d]:
    """
    Create orbit trajectory traces.
    
    Parameters:
    -----------
    orbit_visualizer : OrbitVisualizer
        Orbit visualizer with orbit data
        
    Returns:
    --------
    traces : list
        List of orbit traces
    """
    
    traces = []
    
    for name, orbit in orbit_visualizer.orbits.items():
        points = orbit['points']
        
        trace = go.Scatter3d(
            x=points[:, 0],
            y=points[:, 1],
            z=points[:, 2],
            mode='lines',
            line=dict(
                color=orbit['color'],
                width=orbit['width']
            ),
            name=f"{name} orbit",
            showlegend=True,
            hovertemplate=f"<b>{name} Orbit</b><br>" +
                         "Position: (%{x:.2f}, %{y:.2f}, %{z:.2f}) AU<br>" +
                         "<extra></extra>"
        )
        traces.append(trace)
    
    return traces

def create_spiral_traces(orbit_visualizer) -> List[go.Scatter3d]:
    """
    Create φ-spiral clock traces.
    
    Parameters:
    -----------
    orbit_visualizer : OrbitVisualizer
        Orbit visualizer with spiral data
        
    Returns:
    --------
    traces : list
        List of spiral traces
    """
    
    traces = []
    
    for name, spiral in orbit_visualizer.spirals.items():
        points = spiral['points']
        
        trace = go.Scatter3d(
            x=points[:, 0],
            y=points[:, 1],
            z=points[:, 2],
            mode='lines',
            line=dict(
                color=spiral['color'],
                width=spiral['width']
            ),
            name=f"{name} φ-clock",
            showlegend=True,
            hovertemplate=f"<b>{name} φ-Clock</b><br>" +
                         "τ = %{customdata:.3f}<br>" +
                         "Position: (%{x:.3f}, %{y:.3f}, %{z:.3f}) AU<br>" +
                         "<extra></extra>",
            customdata=[spiral['tau']] * len(points)
        )
        traces.append(trace)
    
    return traces

class SegmentedSpacetimeVisualizer:
    """
    Main visualization class for segmented spacetime solar system.
    """
    
    def __init__(self, title: str = "Segmented Spacetime — Solar System Mesh"):
        self.title = title
        self.traces = []
        self.layout_config = {}
        
    def add_mesh(self, vertices: np.ndarray, faces: np.ndarray,
                field_data: Dict[str, np.ndarray], 
                default_field: str = "N") -> None:
        """
        Add segmented spacetime mesh.
        
        Parameters:
        -----------
        vertices : np.ndarray
            Mesh vertices
        faces : np.ndarray
            Mesh faces
        field_data : dict
            Dictionary of field arrays (N, tau, n)
        default_field : str
            Default field to display
        """
        
        self.vertices = vertices
        self.faces = faces
        self.field_data = field_data
        
        # Create mesh trace for default field
        mesh_trace = create_mesh_trace(
            vertices, faces, field_data[default_field],
            name=default_field
        )
        
        self.traces.append(mesh_trace)
        
    def add_bodies(self, catalog: pd.DataFrame, positions: np.ndarray) -> None:
        """
        Add celestial bodies.
        
        Parameters:
        -----------
        catalog : DataFrame
            Body catalog
        positions : np.ndarray
            Body positions
        """
        
        # Body colors
        body_colors = {
            'Sun': 'yellow',
            'Mercury': 'gray', 
            'Venus': 'orange',
            'Earth': 'blue',
            'Mars': 'red',
            'Jupiter': 'brown',
            'Saturn': 'gold',
            'Uranus': 'cyan',
            'Neptune': 'darkblue'
        }
        
        colors = [body_colors.get(name, 'white') for name in catalog['name']]
        
        body_trace = create_body_trace(
            positions, 
            catalog['name'].tolist(),
            catalog['mass_kg'].values,
            catalog['radius_km'].values,
            colors
        )
        
        self.traces.append(body_trace)
        
    def add_orbits(self, orbit_visualizer) -> None:
        """
        Add orbit trajectories and φ-spirals.
        
        Parameters:
        -----------
        orbit_visualizer : OrbitVisualizer
            Orbit visualizer object
        """
        
        # Add orbit traces
        orbit_traces = create_orbit_traces(orbit_visualizer)
        self.traces.extend(orbit_traces)
        
        # Add spiral traces
        spiral_traces = create_spiral_traces(orbit_visualizer)
        self.traces.extend(spiral_traces)
        
    def create_figure(self, width: int = 1200, height: int = 800) -> go.Figure:
        """
        Create complete Plotly figure.
        
        Parameters:
        -----------
        width, height : int
            Figure dimensions
            
        Returns:
        --------
        fig : go.Figure
            Complete Plotly figure
        """
        
        fig = go.Figure(data=self.traces)
        
        # Layout configuration
        fig.update_layout(
            title=dict(
                text=self.title,
                x=0.5,
                font=dict(size=20, color='white')
            ),
            scene=dict(
                aspectmode="data",
                bgcolor="black",
                xaxis=dict(
                    title="X (AU)",
                    gridcolor="gray",
                    zerolinecolor="gray",
                    title_font=dict(color='white'),
                    tickfont=dict(color='white')
                ),
                yaxis=dict(
                    title="Y (AU)", 
                    gridcolor="gray",
                    zerolinecolor="gray",
                    title_font=dict(color='white'),
                    tickfont=dict(color='white')
                ),
                zaxis=dict(
                    title="Z (AU)",
                    gridcolor="gray", 
                    zerolinecolor="gray",
                    title_font=dict(color='white'),
                    tickfont=dict(color='white')
                ),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.0),
                    center=dict(x=0, y=0, z=0)
                )
            ),
            width=width,
            height=height,
            paper_bgcolor="black",
            plot_bgcolor="black",
            font=dict(color='white'),
            legend=dict(
                bgcolor="rgba(0,0,0,0.5)",
                bordercolor="white",
                borderwidth=1,
                font=dict(color='white')
            )
        )
        
        return fig
        
    def save_html(self, filename: str, include_plotlyjs: str = "cdn") -> None:
        """
        Save visualization as HTML file.
        
        Parameters:
        -----------
        filename : str
            Output filename
        include_plotlyjs : str
            How to include Plotly.js ("cdn", "inline", etc.)
        """
        
        fig = self.create_figure()
        fig.write_html(filename, include_plotlyjs=include_plotlyjs)
        print(f"Saved visualization to {filename}")

def create_interactive_dashboard(field_calculator, catalog: pd.DataFrame, 
                               positions: np.ndarray, vertices: np.ndarray,
                               faces: np.ndarray) -> dash.Dash:
    """
    Create interactive Dash dashboard with parameter controls.
    
    Parameters:
    -----------
    field_calculator : SegmentedSpacetimeField
        Field calculator
    catalog : DataFrame
        Body catalog
    positions : np.ndarray
        Body positions
    vertices : np.ndarray
        Mesh vertices
    faces : np.ndarray
        Mesh faces
        
    Returns:
    --------
    app : dash.Dash
        Dash application
    """
    
    app = dash.Dash(__name__)
    
    # Initial field calculation
    N, tau, n = field_calculator.compute_all_fields(vertices)
    
    app.layout = html.Div([
        html.H1("Segmented Spacetime — Interactive Solar System", 
                style={'textAlign': 'center', 'color': 'white'}),
        
        html.Div([
            html.Div([
                html.Label("Field Display:", style={'color': 'white'}),
                dcc.Dropdown(
                    id='field-selector',
                    options=[
                        {'label': 'Segment Density N(x)', 'value': 'N'},
                        {'label': 'Time Dilation τ(x)', 'value': 'tau'},
                        {'label': 'Refractive Index n(x)', 'value': 'n'}
                    ],
                    value='N',
                    style={'backgroundColor': '#333', 'color': 'black'}
                )
            ], style={'width': '30%', 'display': 'inline-block'}),
            
            html.Div([
                html.Label("α (Time Coupling):", style={'color': 'white'}),
                dcc.Slider(
                    id='alpha-slider',
                    min=0.1, max=3.0, step=0.1, value=1.0,
                    marks={i: str(i) for i in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], style={'width': '30%', 'display': 'inline-block'}),
            
            html.Div([
                html.Label("κ (Refractive Coupling):", style={'color': 'white'}),
                dcc.Slider(
                    id='kappa-slider',
                    min=0.001, max=0.1, step=0.001, value=0.015,
                    marks={i: f"{i:.3f}" for i in [0.005, 0.015, 0.025, 0.05, 0.1]},
                    tooltip={"placement": "bottom", "always_visible": True}
                )
            ], style={'width': '30%', 'display': 'inline-block'})
        ], style={'padding': '20px'}),
        
        dcc.Graph(id='spacetime-mesh', style={'height': '80vh'})
        
    ], style={'backgroundColor': 'black'})
    
    @app.callback(
        Output('spacetime-mesh', 'figure'),
        [Input('field-selector', 'value'),
         Input('alpha-slider', 'value'),
         Input('kappa-slider', 'value')]
    )
    def update_visualization(field_type, alpha, kappa):
        # Update field parameters
        field_calculator.alpha = alpha
        field_calculator.kappa = kappa
        
        # Recalculate fields
        N, tau, n = field_calculator.compute_all_fields(vertices)
        
        # Select field to display
        field_data = {'N': N, 'tau': tau, 'n': n}
        scalars = field_data[field_type]
        
        # Create mesh trace
        mesh_trace = create_mesh_trace(vertices, faces, scalars, name=field_type)
        
        # Create body trace
        body_colors = {
            'Sun': 'yellow', 'Mercury': 'gray', 'Venus': 'orange', 'Earth': 'blue',
            'Mars': 'red', 'Jupiter': 'brown', 'Saturn': 'gold', 
            'Uranus': 'cyan', 'Neptune': 'darkblue'
        }
        colors = [body_colors.get(name, 'white') for name in catalog['name']]
        
        body_trace = create_body_trace(
            positions, catalog['name'].tolist(),
            catalog['mass_kg'].values, catalog['radius_km'].values, colors
        )
        
        # Create figure
        fig = go.Figure(data=[mesh_trace, body_trace])
        
        fig.update_layout(
            title=f"Segmented Spacetime — {field_type}(x) Field",
            scene=dict(
                aspectmode="data",
                bgcolor="black",
                xaxis=dict(title="X (AU)", gridcolor="gray", title_font=dict(color='white')),
                yaxis=dict(title="Y (AU)", gridcolor="gray", title_font=dict(color='white')),
                zaxis=dict(title="Z (AU)", gridcolor="gray", title_font=dict(color='white')),
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.0))
            ),
            paper_bgcolor="black",
            plot_bgcolor="black",
            font=dict(color='white'),
            height=600
        )
        
        return fig
    
    return app

if __name__ == "__main__":
    # Test visualization components
    print("Testing visualization components...")
    
    # Create test mesh
    from .icosphere import build_icosphere
    
    vertices, faces = build_icosphere(radius=10.0, subdivisions=3)
    
    # Test field data
    N = np.random.rand(len(vertices)) * 2
    tau = 0.5 + 0.5 * np.random.rand(len(vertices))
    n = 1.0 + 0.05 * np.random.rand(len(vertices))
    
    # Create mesh trace
    mesh_trace = create_mesh_trace(vertices, faces, N, name="N(x)")
    
    print(f"Created mesh trace with {len(vertices)} vertices, {len(faces)} faces")
    
    # Test body trace
    positions = np.array([[0, 0, 0], [5, 0, 0], [10, 0, 0]])
    names = ['Sun', 'Earth', 'Jupiter']
    masses = np.array([1.989e30, 5.972e24, 1.898e27])
    radii = np.array([695700, 6371, 69911])
    
    body_trace = create_body_trace(positions, names, masses, radii)
    
    print(f"Created body trace with {len(names)} bodies")
    
    print("Visualization test complete!")
