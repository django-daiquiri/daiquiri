ALTER SCHEMA TAP_SCHEMA OWNER TO daiquiri_data;

ALTER SCHEMA daiquiri_user_user OWNER TO daiquiri_data;
ALTER TABLE daiquiri_user_user.test OWNER TO daiquiri_data;

GRANT USAGE ON SCHEMA daiquiri_archive TO daiquiri_data;
GRANT SELECT ON ALL TABLES IN SCHEMA daiquiri_archive TO daiquiri_data;

GRANT USAGE ON SCHEMA daiquiri_data_sim TO daiquiri_data;
GRANT SELECT ON ALL TABLES IN SCHEMA daiquiri_data_sim TO daiquiri_data;

GRANT USAGE ON SCHEMA daiquiri_data_obs TO daiquiri_data;
GRANT SELECT ON ALL TABLES IN SCHEMA daiquiri_data_obs TO daiquiri_data;
