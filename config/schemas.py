"""
Enhanced database schemas and metadata for the France Services SQL Agent.
This file contains detailed schema information for the PostgreSQL database.
REPLACES config/schemas.py with correct France Services schema
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

# Enhanced table schemas with detailed business context
TABLE_SCHEMAS = {
    "maisons_france_services": {
        "description": "France Services offices and locations",
        "primary_key": "id",
        "business_context": "Physical locations providing government services to citizens - contains office details, services offered, and location information",
        "common_queries": ["office analysis", "regional coverage", "service availability", "office locations"],
        "columns": {
            "id": {
                "type": "INTEGER",
                "description": "Unique identifier for each France Services office",
                "is_primary_key": True,
                "business_meaning": "Primary key for office records"
            },
            "nom": {
                "type": "VARCHAR(255)",
                "description": "Name of the France Services office",
                "business_meaning": "Official name of the service center"
            },
            "adresse": {
                "type": "TEXT",
                "description": "Full address of the office",
                "business_meaning": "Physical location for citizen visits"
            },
            "code_postal": {
                "type": "VARCHAR(10)",
                "description": "Postal code of the office location",
                "business_meaning": "Geographic identifier for regional analysis",
                "is_geographic": True
            },
            "ville": {
                "type": "VARCHAR(100)",
                "description": "City where the office is located",
                "business_meaning": "Urban location for geographic analysis",
                "is_geographic": True
            },
            "departement": {
                "type": "VARCHAR(100)",
                "description": "Department (administrative division) of the office",
                "business_meaning": "Administrative geographic division",
                "is_geographic": True
            },
            "region": {
                "type": "VARCHAR(100)",
                "description": "Region where the office is located",
                "business_meaning": "Large geographic region for territorial analysis",
                "is_geographic": True
            },
            "latitude": {
                "type": "DECIMAL(10,8)",
                "description": "GPS latitude coordinate",
                "business_meaning": "Precise geographic location for mapping",
                "is_geographic": True
            },
            "longitude": {
                "type": "DECIMAL(11,8)",
                "description": "GPS longitude coordinate",
                "business_meaning": "Precise geographic location for mapping",
                "is_geographic": True
            },
            "type_structure": {
                "type": "VARCHAR(50)",
                "description": "Type of organization managing the office",
                "business_meaning": "Administrative structure type (collectivite, association, etc.)"
            },
            "date_ouverture": {
                "type": "DATE",
                "description": "Date when the office opened",
                "business_meaning": "Opening date for historical analysis",
                "is_temporal": True
            },
            "nb_conseillers": {
                "type": "INTEGER",
                "description": "Number of advisors working at the office",
                "business_meaning": "Staffing level for capacity analysis",
                "aggregatable": True
            },
            "services_disponibles": {
                "type": "TEXT",
                "description": "List of services available (pipe-separated)",
                "business_meaning": "Services offered to citizens"
            },
            "population_desservie": {
                "type": "INTEGER",
                "description": "Population served by this office",
                "business_meaning": "Catchment area population for coverage analysis",
                "aggregatable": True
            },
            "statut": {
                "type": "VARCHAR(20)",
                "description": "Current status of the office",
                "business_meaning": "Operational status (active, inactive, etc.)"
            }
        }
    },
    "usagers": {
        "description": "Citizens using France Services",
        "primary_key": "id",
        "business_context": "Citizens who visit France Services offices - contains demographics and usage patterns",
        "common_queries": ["user demographics", "citizen analysis", "age distribution", "usage patterns"],
        "columns": {
            "id": {
                "type": "INTEGER",
                "description": "Unique identifier for each citizen user",
                "is_primary_key": True,
                "business_meaning": "Primary key for citizen records"
            },
            "age": {
                "type": "INTEGER",
                "description": "Age of the citizen in years",
                "business_meaning": "Age for demographic analysis and service targeting",
                "aggregatable": True
            },
            "genre": {
                "type": "VARCHAR(10)",
                "description": "Gender of the citizen (M/F)",
                "business_meaning": "Gender for demographic analysis"
            },
            "situation_familiale": {
                "type": "VARCHAR(50)",
                "description": "Family situation (married, single, etc.)",
                "business_meaning": "Family status affecting service needs"
            },
            "niveau_numerique": {
                "type": "VARCHAR(20)",
                "description": "Digital literacy level (debutant, intermediaire, avance)",
                "business_meaning": "Digital skills level for service delivery planning"
            },
            "code_postal": {
                "type": "VARCHAR(10)",
                "description": "Postal code of citizen's residence",
                "business_meaning": "Geographic location for territorial analysis",
                "is_geographic": True
            },
            "ville": {
                "type": "VARCHAR(100)",
                "description": "City of citizen's residence",
                "business_meaning": "Residential location for geographic analysis",
                "is_geographic": True
            },
            "date_inscription": {
                "type": "DATE",
                "description": "Date when the citizen first registered",
                "business_meaning": "Registration date for user growth analysis",
                "is_temporal": True
            },
            "frequence_visite": {
                "type": "VARCHAR(20)",
                "description": "Visit frequency (regulier, occasionnel, nouveau)",
                "business_meaning": "Usage pattern for service planning"
            }
        }
    },
    "demandes": {
        "description": "Service requests made by citizens",
        "primary_key": "id",
        "business_context": "All service requests submitted by citizens - core transaction data with service details, processing times, and satisfaction",
        "common_queries": ["request analysis", "service demand", "satisfaction tracking", "processing times", "workload analysis"],
        "columns": {
            "id": {
                "type": "INTEGER",
                "description": "Unique identifier for each service request",
                "is_primary_key": True,
                "business_meaning": "Primary key for request records"
            },
            "usager_id": {
                "type": "INTEGER",
                "description": "Reference to the citizen making the request",
                "foreign_key": "usagers.id",
                "business_meaning": "Links request to citizen information"
            },
            "maison_fs_id": {
                "type": "INTEGER",
                "description": "Reference to the France Services office handling the request",
                "foreign_key": "maisons_france_services.id",
                "business_meaning": "Links request to service location"
            },
            "date_demande": {
                "type": "TIMESTAMP",
                "description": "Date and time when the request was submitted",
                "business_meaning": "Request timestamp for temporal analysis",
                "is_temporal": True
            },
            "type_service": {
                "type": "VARCHAR(100)",
                "description": "Type of service requested (emploi, retraite, famille, etc.)",
                "business_meaning": "Service category for demand analysis"
            },
            "organisme_concerne": {
                "type": "VARCHAR(100)",
                "description": "Government organization involved (pole_emploi, caf, etc.)",
                "business_meaning": "Responsible government agency"
            },
            "canal": {
                "type": "VARCHAR(20)",
                "description": "Service delivery channel (physique, telephone, visio, numerique)",
                "business_meaning": "How the service was delivered"
            },
            "duree_traitement": {
                "type": "INTEGER",
                "description": "Processing time in minutes",
                "business_meaning": "Time spent handling the request",
                "aggregatable": True,
                "unit": "minutes"
            },
            "satisfaction_score": {
                "type": "INTEGER",
                "description": "Citizen satisfaction score (1-5)",
                "business_meaning": "Service quality measurement",
                "aggregatable": True
            },
            "resolu": {
                "type": "BOOLEAN",
                "description": "Whether the request was resolved",
                "business_meaning": "Request resolution status"
            },
            "conseiller_id": {
                "type": "INTEGER",
                "description": "Reference to the advisor who handled the request",
                "foreign_key": "conseillers.id",
                "business_meaning": "Links request to staff member"
            },
            "complexite": {
                "type": "VARCHAR(20)",
                "description": "Complexity level (simple, moyen, complexe)",
                "business_meaning": "Request difficulty for workload planning"
            },
            "suivi_necessaire": {
                "type": "BOOLEAN",
                "description": "Whether follow-up is needed",
                "business_meaning": "Indicates if additional action required"
            }
        }
    },
    "conseillers": {
        "description": "Advisors working in France Services offices",
        "primary_key": "id",
        "business_context": "Staff members providing services to citizens - contains advisor details, specialties, and employment information",
        "common_queries": ["staff analysis", "expertise mapping", "workload distribution", "advisor performance"],
        "columns": {
            "id": {
                "type": "INTEGER",
                "description": "Unique identifier for each advisor",
                "is_primary_key": True,
                "business_meaning": "Primary key for advisor records"
            },
            "nom": {
                "type": "VARCHAR(100)",
                "description": "Last name of the advisor",
                "business_meaning": "Advisor identification"
            },
            "prenom": {
                "type": "VARCHAR(100)",
                "description": "First name of the advisor",
                "business_meaning": "Advisor identification"
            },
            "maison_fs_id": {
                "type": "INTEGER",
                "description": "Reference to the France Services office where they work",
                "foreign_key": "maisons_france_services.id",
                "business_meaning": "Work location assignment"
            },
            "specialite": {
                "type": "VARCHAR(50)",
                "description": "Area of expertise",
                "business_meaning": "Professional specialty for service matching"
            },
            "date_embauche": {
                "type": "DATE",
                "description": "Date when the advisor was hired",
                "business_meaning": "Employment start date for tenure analysis",
                "is_temporal": True
            },
            "temps_travail": {
                "type": "VARCHAR(20)",
                "description": "Work schedule type (temps_plein, temps_partiel)",
                "business_meaning": "Employment type for capacity planning"
            },
            "niveau_experience": {
                "type": "VARCHAR(20)",
                "description": "Experience level (junior, senior, expert)",
                "business_meaning": "Skill level for service assignment"
            },
            "statut": {
                "type": "VARCHAR(20)",
                "description": "Current employment status",
                "business_meaning": "Active/inactive status"
            }
        }
    },
    "plannings": {
        "description": "Office scheduling and capacity planning",
        "primary_key": "id",
        "business_context": "Daily schedules and staffing for France Services offices",
        "common_queries": ["capacity analysis", "staffing levels", "operating hours"],
        "columns": {
            "id": {
                "type": "INTEGER",
                "description": "Unique identifier for each schedule entry",
                "is_primary_key": True,
                "business_meaning": "Primary key for schedule records"
            },
            "maison_fs_id": {
                "type": "INTEGER",
                "description": "Reference to the France Services office",
                "foreign_key": "maisons_france_services.id",
                "business_meaning": "Office being scheduled"
            },
            "date": {
                "type": "DATE",
                "description": "Date for this schedule",
                "business_meaning": "Specific date for capacity planning",
                "is_temporal": True
            },
            "jour_semaine": {
                "type": "VARCHAR(20)",
                "description": "Day of the week",
                "business_meaning": "Weekly pattern analysis"
            },
            "heure_ouverture": {
                "type": "DECIMAL(3,1)",
                "description": "Opening time (24h format)",
                "business_meaning": "Service availability start time"
            },
            "heure_fermeture": {
                "type": "DECIMAL(3,1)",
                "description": "Closing time (24h format)",
                "business_meaning": "Service availability end time"
            },
            "nb_conseillers_prevus": {
                "type": "INTEGER",
                "description": "Number of advisors scheduled",
                "business_meaning": "Planned staffing level",
                "aggregatable": True
            },
            "nb_conseillers_presents": {
                "type": "INTEGER",
                "description": "Number of advisors actually present",
                "business_meaning": "Actual staffing level",
                "aggregatable": True
            },
            "fermeture_exceptionnelle": {
                "type": "BOOLEAN",
                "description": "Whether office was exceptionally closed",
                "business_meaning": "Unplanned closure indicator"
            }
        }
    },
    "statistiques_mensuelles": {
        "description": "Monthly performance statistics for each office",
        "primary_key": "id",
        "business_context": "Aggregated monthly data for performance monitoring and reporting",
        "common_queries": ["monthly performance", "trends analysis", "KPI tracking"],
        "columns": {
            "id": {
                "type": "INTEGER",
                "description": "Unique identifier for each monthly record",
                "is_primary_key": True,
                "business_meaning": "Primary key for monthly statistics"
            },
            "maison_fs_id": {
                "type": "INTEGER",
                "description": "Reference to the France Services office",
                "foreign_key": "maisons_france_services.id",
                "business_meaning": "Office being measured"
            },
            "mois": {
                "type": "INTEGER",
                "description": "Month (1-12)",
                "business_meaning": "Month for temporal analysis",
                "is_temporal": True
            },
            "annee": {
                "type": "INTEGER",
                "description": "Year",
                "business_meaning": "Year for temporal analysis",
                "is_temporal": True
            },
            "nb_demandes": {
                "type": "INTEGER",
                "description": "Total number of requests that month",
                "business_meaning": "Monthly request volume",
                "aggregatable": True
            },
            "nb_demandes_resolues": {
                "type": "INTEGER",
                "description": "Number of requests resolved that month",
                "business_meaning": "Monthly resolution count",
                "aggregatable": True
            },
            "temps_moyen_resolution": {
                "type": "INTEGER",
                "description": "Average resolution time in minutes",
                "business_meaning": "Monthly average processing time",
                "aggregatable": True,
                "unit": "minutes"
            },
            "satisfaction_moyenne": {
                "type": "DECIMAL(3,2)",
                "description": "Average satisfaction score for the month",
                "business_meaning": "Monthly customer satisfaction",
                "aggregatable": True
            },
            "nb_usagers_uniques": {
                "type": "INTEGER",
                "description": "Number of unique citizens served",
                "business_meaning": "Monthly unique user count",
                "aggregatable": True
            },
            "nb_nouveaux_usagers": {
                "type": "INTEGER",
                "description": "Number of new citizens registered",
                "business_meaning": "Monthly new user acquisition",
                "aggregatable": True
            },
            "taux_retour_usagers": {
                "type": "DECIMAL(3,2)",
                "description": "Percentage of returning citizens",
                "business_meaning": "User retention rate"
            }
        }
    }
}

# Enhanced relationship definitions with join patterns
TABLE_RELATIONSHIPS = {
    "maisons_france_services": {
        "joins_to": {
            "demandes": {
                "join_key": "id = maison_fs_id",
                "relationship": "one_to_many",
                "purpose": "Get all requests for an office",
                "join_sql": "maisons_france_services m JOIN demandes d ON m.id = d.maison_fs_id"
            },
            "conseillers": {
                "join_key": "id = maison_fs_id",
                "relationship": "one_to_many",
                "purpose": "Get all advisors for an office",
                "join_sql": "maisons_france_services m JOIN conseillers c ON m.id = c.maison_fs_id"
            },
            "plannings": {
                "join_key": "id = maison_fs_id",
                "relationship": "one_to_many",
                "purpose": "Get office schedules",
                "join_sql": "maisons_france_services m JOIN plannings p ON m.id = p.maison_fs_id"
            },
            "statistiques_mensuelles": {
                "join_key": "id = maison_fs_id",
                "relationship": "one_to_many",
                "purpose": "Get monthly statistics for an office",
                "join_sql": "maisons_france_services m JOIN statistiques_mensuelles s ON m.id = s.maison_fs_id"
            }
        }
    },
    "usagers": {
        "joins_to": {
            "demandes": {
                "join_key": "id = usager_id",
                "relationship": "one_to_many",
                "purpose": "Get all requests by a citizen",
                "join_sql": "usagers u JOIN demandes d ON u.id = d.usager_id"
            }
        }
    },
    "demandes": {
        "joins_to": {
            "usagers": {
                "join_key": "usager_id = id",
                "relationship": "many_to_one",
                "purpose": "Get citizen information for requests",
                "join_sql": "demandes d JOIN usagers u ON d.usager_id = u.id"
            },
            "maisons_france_services": {
                "join_key": "maison_fs_id = id",
                "relationship": "many_to_one",
                "purpose": "Get office information for requests",
                "join_sql": "demandes d JOIN maisons_france_services m ON d.maison_fs_id = m.id"
            },
            "conseillers": {
                "join_key": "conseiller_id = id",
                "relationship": "many_to_one",
                "purpose": "Get advisor information for requests",
                "join_sql": "demandes d JOIN conseillers c ON d.conseiller_id = c.id"
            }
        }
    },
    "conseillers": {
        "joins_to": {
            "maisons_france_services": {
                "join_key": "maison_fs_id = id",
                "relationship": "many_to_one",
                "purpose": "Get office information for advisors",
                "join_sql": "conseillers c JOIN maisons_france_services m ON c.maison_fs_id = m.id"
            },
            "demandes": {
                "join_key": "id = conseiller_id",
                "relationship": "one_to_many",
                "purpose": "Get all requests handled by an advisor",
                "join_sql": "conseillers c JOIN demandes d ON c.id = d.conseiller_id"
            }
        }
    }
}

# Enhanced query patterns with business context
QUERY_PATTERNS = {
    "citizen_analysis": {
        "keywords": ["usager", "citoyen", "client", "utilisateur", "demographics", "citizen", "user"],
        "requires_tables": ["usagers"],
        "key_columns": ["age", "genre", "ville", "niveau_numerique", "frequence_visite"],
        "common_joins": "usagers u LEFT JOIN demandes d ON u.id = d.usager_id",
        "example_sql": "SELECT u.ville, COUNT(d.id) as nb_demandes FROM usagers u LEFT JOIN demandes d ON u.id = d.usager_id GROUP BY u.ville"
    },
    "office_analysis": {
        "keywords": ["maison", "bureau", "office", "location", "antenne", "structure"],
        "requires_tables": ["maisons_france_services"],
        "key_columns": ["nom", "ville", "region", "nb_conseillers", "services_disponibles", "population_desservie"],
        "common_joins": "maisons_france_services m LEFT JOIN demandes d ON m.id = d.maison_fs_id",
        "example_sql": "SELECT m.region, COUNT(m.id) as nb_maisons FROM maisons_france_services m GROUP BY m.region"
    },
    "service_demand_analysis": {
        "keywords": ["demande", "service", "request", "prestation", "traitement"],
        "requires_tables": ["demandes"],
        "key_columns": ["type_service", "organisme_concerne", "canal", "duree_traitement", "satisfaction_score"],
        "aggregations": ["COUNT", "AVG", "SUM"],
        "example_sql": "SELECT type_service, COUNT(*) as nb_demandes, AVG(satisfaction_score) as satisfaction FROM demandes GROUP BY type_service"
    },
    "staff_analysis": {
        "keywords": ["conseiller", "advisor", "staff", "personnel", "employe"],
        "requires_tables": ["conseillers"],
        "key_columns": ["nom", "prenom", "specialite", "niveau_experience", "temps_travail"],
        "common_joins": "conseillers c LEFT JOIN maisons_france_services m ON c.maison_fs_id = m.id",
        "example_sql": "SELECT c.specialite, COUNT(*) as nb_conseillers FROM conseillers c GROUP BY c.specialite"
    },
    "temporal_analysis": {
        "keywords": ["temps", "date", "periode", "recent", "mois", "annee", "daily", "monthly"],
        "requires_tables": ["demandes", "statistiques_mensuelles"],
        "key_columns": ["date_demande", "mois", "annee"],
        "common_filters": "WHERE date_demande >= NOW() - INTERVAL '30 days'",
        "example_sql": "SELECT DATE(date_demande) as jour, COUNT(*) as nb_demandes FROM demandes WHERE date_demande >= NOW() - INTERVAL '7 days' GROUP BY DATE(date_demande)"
    },
    "geographic_analysis": {
        "keywords": ["region", "ville", "departement", "geographic", "territorial", "location"],
        "requires_tables": ["maisons_france_services", "usagers"],
        "key_columns": ["region", "ville", "departement", "code_postal"],
        "example_sql": "SELECT m.region, COUNT(d.id) as nb_demandes FROM maisons_france_services m JOIN demandes d ON m.id = d.maison_fs_id GROUP BY m.region"
    },
    "performance_analysis": {
        "keywords": ["performance", "satisfaction", "efficacite", "qualite", "kpi", "statistique"],
        "requires_tables": ["demandes", "statistiques_mensuelles"],
        "key_columns": ["satisfaction_score", "duree_traitement", "resolu", "satisfaction_moyenne"],
        "aggregations": ["AVG", "COUNT", "SUM"],
        "example_sql": "SELECT AVG(satisfaction_score) as satisfaction_moyenne, AVG(duree_traitement) as duree_moyenne FROM demandes WHERE resolu = true"
    }
}

# Business scenarios with SQL templates for France Services
BUSINESS_SCENARIOS = {
    "top_offices_by_requests": {
        "description": "Rank offices by number of requests handled",
        "keywords": ["top offices", "busiest offices", "most requests", "office ranking"],
        "sql_template": """
        SELECT 
            m.nom,
            m.ville,
            m.region,
            COUNT(d.id) as nb_demandes,
            AVG(d.satisfaction_score) as satisfaction_moyenne
        FROM maisons_france_services m
        LEFT JOIN demandes d ON m.id = d.maison_fs_id
        GROUP BY m.id, m.nom, m.ville, m.region
        ORDER BY nb_demandes DESC
        LIMIT {limit}
        """,
        "required_tables": ["maisons_france_services", "demandes"]
    },
    "citizen_demographics": {
        "description": "Analyze citizen demographics and usage patterns",
        "keywords": ["demographics", "age distribution", "citizen analysis", "user profile"],
        "sql_template": """
        SELECT 
            u.ville,
            u.genre,
            AVG(u.age) as age_moyen,
            COUNT(u.id) as nb_usagers,
            COUNT(d.id) as nb_demandes
        FROM usagers u
        LEFT JOIN demandes d ON u.id = d.usager_id
        GROUP BY u.ville, u.genre
        ORDER BY nb_demandes DESC
        LIMIT {limit}
        """,
        "required_tables": ["usagers", "demandes"]
    },
    "service_demand_trends": {
        "description": "Analyze service demand by type and trends",
        "keywords": ["service demand", "popular services", "service trends", "type analysis"],
        "sql_template": """
        SELECT 
            type_service,
            organisme_concerne,
            COUNT(*) as nb_demandes,
            AVG(satisfaction_score) as satisfaction_moyenne,
            AVG(duree_traitement) as duree_moyenne
        FROM demandes
        WHERE date_demande >= NOW() - INTERVAL '{days} days'
        GROUP BY type_service, organisme_concerne
        ORDER BY nb_demandes DESC
        LIMIT {limit}
        """,
        "required_tables": ["demandes"]
    },
    "advisor_workload": {
        "description": "Analyze advisor workload and performance",
        "keywords": ["advisor performance", "staff workload", "conseiller analysis"],
        "sql_template": """
        SELECT 
            c.nom,
            c.prenom,
            c.specialite,
            m.nom as office_name,
            COUNT(d.id) as nb_demandes_traitees,
            AVG(d.satisfaction_score) as satisfaction_moyenne
        FROM conseillers c
        LEFT JOIN demandes d ON c.id = d.conseiller_id
        LEFT JOIN maisons_france_services m ON c.maison_fs_id = m.id
        GROUP BY c.id, c.nom, c.prenom, c.specialite, m.nom
        ORDER BY nb_demandes_traitees DESC
        LIMIT {limit}
        """,
        "required_tables": ["conseillers", "demandes", "maisons_france_services"]
    },
    "regional_coverage": {
        "description": "Analyze service coverage by region",
        "keywords": ["regional analysis", "territorial coverage", "geographic distribution"],
        "sql_template": """
        SELECT 
            m.region,
            COUNT(DISTINCT m.id) as nb_offices,
            COUNT(d.id) as nb_demandes,
            SUM(m.population_desservie) as population_totale,
            AVG(d.satisfaction_score) as satisfaction_moyenne
        FROM maisons_france_services m
        LEFT JOIN demandes d ON m.id = d.maison_fs_id
        GROUP BY m.region
        ORDER BY nb_demandes DESC
        LIMIT {limit}
        """,
        "required_tables": ["maisons_france_services", "demandes"]
    }
}

def get_table_schema(table_name: str) -> Dict[str, Any]:
    """Get schema for a specific table."""
    return TABLE_SCHEMAS.get(table_name, {})

def get_all_table_schemas() -> Dict[str, Dict[str, Any]]:
    """Get all table schemas."""
    return TABLE_SCHEMAS

def get_table_relationships() -> Dict[str, Dict[str, Any]]:
    """Get table relationships."""
    return TABLE_RELATIONSHIPS

def get_query_patterns() -> Dict[str, Dict[str, Any]]:
    """Get query patterns."""
    return QUERY_PATTERNS

def get_business_scenarios() -> Dict[str, Dict[str, Any]]:
    """Get business scenarios."""
    return BUSINESS_SCENARIOS

def list_tables() -> List[str]:
    """List all available tables."""
    return list(TABLE_SCHEMAS.keys())

def get_columns_with_names(table_name: str) -> List[str]:
    """Get columns that likely contain names or identifiers."""
    table_schema = TABLE_SCHEMAS.get(table_name, {})
    columns = table_schema.get('columns', {})

    name_columns = []
    for col_name, col_info in columns.items():
        if any(keyword in col_name.lower() for keyword in ['nom', 'name', 'prenom', 'firstname']):
            name_columns.append(col_name)

    return name_columns

def find_customer_equivalent_tables() -> List[str]:
    """Find tables that contain customer/user information."""
    customer_tables = []
    for table_name, schema in TABLE_SCHEMAS.items():
        business_context = schema.get('business_context', '').lower()
        if any(keyword in business_context for keyword in ['citizen', 'user', 'customer', 'usager']):
            customer_tables.append(table_name)
    return customer_tables

def get_name_queries_for_table(table_name: str, limit: int = 10) -> str:
    """Generate appropriate SQL query to get names from a table."""
    name_columns = get_columns_with_names(table_name)

    if table_name == "usagers":
        # Usagers table doesn't have names, so we use ID and demographics
        return f"""
        SELECT 
            'Usager ' || id as identifier,
            ville,
            age,
            genre
        FROM {table_name}
        ORDER BY RANDOM()
        LIMIT {limit}
        """
    elif table_name == "conseillers":
        # Conseillers has actual names
        return f"""
        SELECT 
            nom || ' ' || prenom as full_name,
            specialite,
            niveau_experience
        FROM {table_name}
        ORDER BY RANDOM()
        LIMIT {limit}
        """
    elif table_name == "maisons_france_services":
        # Office names
        return f"""
        SELECT 
            nom as office_name,
            ville,
            region
        FROM {table_name}
        ORDER BY RANDOM()
        LIMIT {limit}
        """
    else:
        # Generic fallback
        if name_columns:
            columns_str = ', '.join(name_columns)
            return f"SELECT {columns_str} FROM {table_name} ORDER BY RANDOM() LIMIT {limit}"
        else:
            return f"SELECT * FROM {table_name} ORDER BY RANDOM() LIMIT {limit}"

def get_column_info(table_name: str, column_name: str) -> Dict[str, Any]:
    """Get detailed information about a specific column."""
    table_schema = TABLE_SCHEMAS.get(table_name, {})
    columns = table_schema.get('columns', {})
    return columns.get(column_name, {})

def get_foreign_keys(table_name: str) -> List[Dict[str, str]]:
    """Get foreign key relationships for a table."""
    foreign_keys = []
    table_schema = TABLE_SCHEMAS.get(table_name, {})
    columns = table_schema.get('columns', {})

    for col_name, col_info in columns.items():
        if 'foreign_key' in col_info:
            foreign_keys.append({
                'column': col_name,
                'references': col_info['foreign_key'],
                'description': col_info.get('business_meaning', '')
            })

    return foreign_keys

def get_aggregatable_columns(table_name: str) -> List[str]:
    """Get columns that can be aggregated (SUM, COUNT, AVG, etc.)."""
    table_schema = TABLE_SCHEMAS.get(table_name, {})
    columns = table_schema.get('columns', {})

    aggregatable = []
    for col_name, col_info in columns.items():
        if col_info.get('aggregatable', False):
            aggregatable.append(col_name)

    return aggregatable

def get_temporal_columns(table_name: str) -> List[str]:
    """Get columns that contain temporal/date information."""
    table_schema = TABLE_SCHEMAS.get(table_name, {})
    columns = table_schema.get('columns', {})

    temporal = []
    for col_name, col_info in columns.items():
        if col_info.get('is_temporal', False):
            temporal.append(col_name)

    return temporal

def get_geographic_columns(table_name: str) -> List[str]:
    """Get columns that contain geographic information."""
    table_schema = TABLE_SCHEMAS.get(table_name, {})
    columns = table_schema.get('columns', {})

    geographic = []
    for col_name, col_info in columns.items():
        if col_info.get('is_geographic', False):
            geographic.append(col_name)

    return geographic

def suggest_query_for_request(user_request: str) -> Dict[str, Any]:
    """Suggest appropriate tables and columns based on user request."""
    user_request_lower = user_request.lower()

    suggestions = {
        'tables': [],
        'columns': [],
        'query_pattern': None,
        'suggested_sql': None
    }

    # Look for customer/user related requests
    if any(keyword in user_request_lower for keyword in ['customer', 'client', 'user', 'people', 'citizen', 'usager', 'nom', 'name']):
        if 'advisor' in user_request_lower or 'conseiller' in user_request_lower or 'staff' in user_request_lower:
            suggestions['tables'] = ['conseillers']
            suggestions['columns'] = ['nom', 'prenom', 'specialite']
            suggestions['suggested_sql'] = get_name_queries_for_table('conseillers')
        else:
            suggestions['tables'] = ['usagers']
            suggestions['columns'] = ['id', 'ville', 'age', 'genre']
            suggestions['suggested_sql'] = get_name_queries_for_table('usagers')

    # Look for office related requests
    elif any(keyword in user_request_lower for keyword in ['office', 'location', 'maison', 'bureau']):
        suggestions['tables'] = ['maisons_france_services']
        suggestions['columns'] = ['nom', 'ville', 'region']
        suggestions['suggested_sql'] = get_name_queries_for_table('maisons_france_services')

    # Look for service/request related queries
    elif any(keyword in user_request_lower for keyword in ['service', 'request', 'demande']):
        suggestions['tables'] = ['demandes']
        suggestions['columns'] = ['type_service', 'organisme_concerne', 'satisfaction_score']
        suggestions['query_pattern'] = 'service_demand_analysis'

    return suggestions