-- Gaia DR3 core: Pflichtspalten + sinnvolle Extras
SELECT
  source_id,
  ra, ra_error,
  dec, dec_error,
  parallax, parallax_error,
  pmra, pmra_error,
  pmdec, pmdec_error,
  radial_velocity, radial_velocity_error,
  phot_g_mean_mag, bp_rp, ruwe
FROM gaiaedr3.gaia_source
-- OPTIONAL: WHERE-Klausel / TOP-Limit setzt der Fetcher via --limit
