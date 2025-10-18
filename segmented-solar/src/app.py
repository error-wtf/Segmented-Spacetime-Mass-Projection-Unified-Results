"""
Main application orchestrator for Segmented Spacetime Solar System Visualization.
Coordinates data fetching, field calculation, and visualization generation.
"""

import argparse
import numpy as np
import pandas as pd
import os
import sys
from typing import Dict, Optional, Tuple
import warnings

# Import local modules
from .icosphere import build_icosphere, mesh_info
from .segments import SegmentedSpacetimeField, create_solar_system_field
from .fetch_gaia import get_local_stellar_environment
from .fetch_vizier import get_complete_solar_system
from .orbits import create_solar_system_orbits
from .viz_plotly import SegmentedSpacetimeVisualizer, create_interactive_dashboard
from .coords import solar_masses_to_kg, kg_to_solar_masses

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore', category=UserWarning)

class SegmentedSolarApp:
    """
    Main application class for segmented spacetime solar system visualization.
    """
    
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.field_calculator = None
        self.catalog = None
        self.positions = None
        self.vertices = None
        self.faces = None
        self.field_data = {}
        
        # Create output directory
        os.makedirs("data/processed", exist_ok=True)
        
    def setup_mesh(self) -> None:
        """Generate icosphere mesh for spacetime visualization."""
        print(f"Generating icosphere mesh (subdivisions={self.args.mesh_subdiv}, radius={self.args.range_au} AU)...")
        
        self.vertices, self.faces = build_icosphere(
            radius=self.args.range_au,
            subdivisions=self.args.mesh_subdiv
        )
        
        info = mesh_info(self.vertices, self.faces)
        print(f"Mesh: {info['num_vertices']} vertices, {info['num_faces']} faces")
        
        # Save mesh data
        np.savetxt("data/processed/mesh_vertices.csv", self.vertices, 
                  delimiter=',', header='x_AU,y_AU,z_AU', comments='')
        np.savetxt("data/processed/mesh_faces.csv", self.faces, 
                  delimiter=',', header='v1,v2,v3', comments='', fmt='%d')
        
    def fetch_astronomical_data(self) -> None:
        """Fetch astronomical data from catalogs."""
        print(f"Fetching Solar System data for epoch {self.args.epoch}...")
        
        # Get Solar System bodies
        self.catalog, self.positions = get_complete_solar_system(
            epoch=self.args.epoch,
            include_asteroids=self.args.include_asteroids,
            include_moons=self.args.include_moons,
            cache_dir="data/raw"
        )
        
        # Optionally fetch GAIA stars for external field
        if self.args.include_gaia:
            print(f"Fetching GAIA stars within {self.args.gaia_maxdist_pc} pc...")
            try:
                star_positions, star_masses, star_catalog = get_local_stellar_environment(
                    maxdist_pc=self.args.gaia_maxdist_pc,
                    gmag_max=self.args.gaia_gmag_max,
                    epoch=self.args.epoch
                )
                
                if len(star_catalog) > 0:
                    # Add stars to catalog with appropriate scaling
                    star_data = []
                    for i, (pos, mass) in enumerate(zip(star_positions, star_masses)):
                        star_data.append({
                            'name': f'Star_{i+1}',
                            'mass_kg': mass * 1.98847e30,  # Solar masses to kg
                            'radius_km': 695700 * (mass**0.8),  # Approximate radius scaling
                            'a_AU': 0, 'e': 0, 'i_deg': 0,
                            'Omega_deg': 0, 'omega_deg': 0, 'M_deg': 0,
                            'period_days': 0
                        })
                    
                    star_df = pd.DataFrame(star_data)
                    self.catalog = pd.concat([self.catalog, star_df], ignore_index=True)
                    self.positions = np.vstack([self.positions, star_positions])
                    
                    print(f"Added {len(star_catalog)} GAIA stars to field calculation")
                    
            except Exception as e:
                print(f"Warning: Could not fetch GAIA data: {e}")
                print("Continuing with Solar System bodies only...")
        
        # Save processed data
        self.catalog.to_csv("data/processed/body_catalog.csv", index=False)
        np.savetxt("data/processed/body_positions.csv", self.positions,
                  delimiter=',', header='x_AU,y_AU,z_AU', comments='')
        
    def setup_field_calculator(self) -> None:
        """Initialize segmented spacetime field calculator."""
        print("Setting up segmented spacetime field calculator...")
        
        # Field parameters
        params = {
            'p': self.args.p,
            'N_bg': self.args.N_bg,
            'N_max': self.args.N_max,
            'alpha': self.args.alpha,
            'kappa': self.args.kappa
        }
        
        self.field_calculator = SegmentedSpacetimeField(params)
        
        # Add bodies to field
        for i, row in self.catalog.iterrows():
            position = self.positions[i]
            
            # Mass scaling (convert to dimensionless units)
            mass_kg = row['mass_kg']
            mass_solar = mass_kg / 1.98847e30
            
            # Radius in AU
            radius_au = row['radius_km'] / 149597870.7
            
            # Natural boundary parameters
            r0 = max(radius_au, 1e-6)  # Softening radius
            r_nb = r0 * 4  # Natural boundary
            delta = r0 * 0.8  # Transition width
            
            # Gamma scaling based on mass
            if row['name'] == 'Sun':
                gamma = 1.0
            else:
                gamma = min(mass_solar, 1.0)  # Cap at solar mass
            
            self.field_calculator.add_body(
                position=position,
                mass_scaled=mass_solar,
                gamma=gamma,
                r0=r0,
                r_nb=r_nb,
                delta=delta,
                name=row['name']
            )
        
        print(f"Added {len(self.catalog)} bodies to field calculator")
        
    def compute_fields(self) -> None:
        """Compute segmented spacetime fields on mesh."""
        print("Computing segmented spacetime fields...")
        
        # Compute all fields
        N, tau, n = self.field_calculator.compute_all_fields(self.vertices)
        
        self.field_data = {
            'N': N,
            'tau': tau,
            'n': n
        }
        
        # Print field statistics
        for field_name, field_values in self.field_data.items():
            print(f"{field_name}: min={field_values.min():.4f}, "
                  f"max={field_values.max():.4f}, "
                  f"mean={field_values.mean():.4f}")
        
        # Save field data
        field_df = pd.DataFrame({
            'x_AU': self.vertices[:, 0],
            'y_AU': self.vertices[:, 1],
            'z_AU': self.vertices[:, 2],
            'N': N,
            'tau': tau,
            'n': n
        })
        field_df.to_csv("data/processed/field_data.csv", index=False)
        
    def create_visualization(self) -> None:
        """Create and save visualization."""
        print("Creating visualization...")
        
        # Initialize visualizer
        visualizer = SegmentedSpacetimeVisualizer(
            title="Segmented Spacetime — Solar System Mesh (φ/π Structure)"
        )
        
        # Add mesh with field data
        visualizer.add_mesh(
            self.vertices, 
            self.faces, 
            self.field_data,
            default_field='N'
        )
        
        # Add celestial bodies
        visualizer.add_bodies(self.catalog, self.positions)
        
        # Add orbits if requested
        if self.args.show_orbits:
            print("Generating orbital trajectories...")
            orbit_viz = create_solar_system_orbits(
                self.catalog, 
                self.positions,
                self.field_calculator
            )
            visualizer.add_orbits(orbit_viz)
        
        # Save HTML visualization
        output_file = "solar_system_segmented.html"
        visualizer.save_html(output_file)
        
        # Create PNG snapshots if requested
        if self.args.save_images:
            print("Saving field visualizations as images...")
            fig = visualizer.create_figure()
            
            for field_name in ['N', 'tau', 'n']:
                # Update mesh with specific field
                fig.data[0].intensity = self.field_data[field_name]
                fig.data[0].name = field_name
                fig.layout.title.text = f"Segmented Spacetime — {field_name}(x) Field"
                
                # Save image
                fig.write_image(f"segmented_spacetime_{field_name}.png", 
                              width=1200, height=800)
        
        print(f"Visualization saved to {output_file}")
        
    def run_interactive_dashboard(self) -> None:
        """Launch interactive Dash dashboard."""
        if not self.args.interactive:
            return
            
        print("Launching interactive dashboard...")
        
        app = create_interactive_dashboard(
            self.field_calculator,
            self.catalog,
            self.positions,
            self.vertices,
            self.faces
        )
        
        app.run_server(
            debug=False,
            host='127.0.0.1',
            port=8050
        )
        
    def run(self) -> None:
        """Execute complete workflow."""
        print("🌌 Segmented Spacetime Solar System Visualization")
        print("=" * 60)
        
        try:
            # Setup mesh
            self.setup_mesh()
            
            # Fetch data
            self.fetch_astronomical_data()
            
            # Setup field calculator
            self.setup_field_calculator()
            
            # Compute fields
            self.compute_fields()
            
            # Create visualization
            self.create_visualization()
            
            # Launch interactive dashboard if requested
            self.run_interactive_dashboard()
            
            print("\n✅ Segmented spacetime visualization complete!")
            print(f"📁 Output files:")
            print(f"   - solar_system_segmented.html (interactive visualization)")
            print(f"   - data/processed/ (mesh and field data)")
            
            if self.args.save_images:
                print(f"   - segmented_spacetime_*.png (field images)")
            
        except Exception as e:
            print(f"\n❌ Error during execution: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

def create_argument_parser() -> argparse.ArgumentParser:
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Segmented Spacetime Solar System Visualization",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Data parameters
    parser.add_argument('--epoch', default='2025-01-01',
                       help='Epoch for planetary positions (YYYY-MM-DD)')
    
    # Mesh parameters
    parser.add_argument('--mesh-subdiv', type=int, default=6,
                       help='Icosphere subdivision level (3-8)')
    parser.add_argument('--range-au', type=float, default=120.0,
                       help='Mesh radius in AU')
    
    # Field model parameters
    parser.add_argument('--alpha', type=float, default=1.0,
                       help='Time dilation coupling parameter')
    parser.add_argument('--kappa', type=float, default=0.015,
                       help='Refractive index coupling parameter')
    parser.add_argument('--p', type=float, default=2.0,
                       help='Power-law index for kernel')
    parser.add_argument('--N-bg', type=float, default=0.0,
                       help='Background segment density')
    parser.add_argument('--N-max', type=float, default=5.0,
                       help='Maximum segment density')
    
    # Data scope
    parser.add_argument('--include-asteroids', action='store_true',
                       help='Include major asteroids')
    parser.add_argument('--include-moons', action='store_true',
                       help='Include major moons')
    parser.add_argument('--include-gaia', action='store_true',
                       help='Include GAIA stars for external field')
    parser.add_argument('--gaia-maxdist-pc', type=float, default=30,
                       help='Maximum distance for GAIA stars (pc)')
    parser.add_argument('--gaia-gmag-max', type=float, default=10,
                       help='Maximum G magnitude for GAIA stars')
    
    # Visualization options
    parser.add_argument('--show-orbits', action='store_true',
                       help='Show orbital trajectories')
    parser.add_argument('--show-spiral-clocks', action='store_true',
                       help='Show φ-spiral clocks around bodies')
    parser.add_argument('--save-images', action='store_true',
                       help='Save PNG images of field visualizations')
    parser.add_argument('--interactive', action='store_true',
                       help='Launch interactive Dash dashboard')
    
    return parser

def main():
    """Main entry point."""
    parser = create_argument_parser()
    args = parser.parse_args()
    
    # Validate arguments
    if args.mesh_subdiv < 3 or args.mesh_subdiv > 8:
        print("Warning: mesh-subdiv should be between 3-8 for reasonable performance")
    
    if args.range_au < 10 or args.range_au > 1000:
        print("Warning: range-au should typically be between 10-1000 AU")
    
    # Create and run application
    app = SegmentedSolarApp(args)
    app.run()

if __name__ == "__main__":
    main()
