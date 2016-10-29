/*******************************************************************************
 * Intersections
 ******************************************************************************/

DROP TABLE IF EXISTS intersections;

CREATE TABLE intersections(
    id integer primary key autoincrement,
    street0 text not null,
    street1 text not null,
    lat real not null,
    lon real not null
);
