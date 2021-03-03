CREATE OR REPLACE FUNCTION dfosm_split_geometry(in x double precision, in y double precision)
    RETURNS table (
        tgt integer,
        src integer,
        geom geometry
                  ) AS
$$
    declare
        geom1 geometry;
        geom2 geometry;
        geom1_start geometry;
        geom1_end geometry;
        geom_point geometry;
        node_source integer;
        node_target integer;

begin
        SELECT st_geometryn(ST_Split(geom_way, line_point), 1) as geom1,
               st_geometryn(ST_Split(geom_way, line_point), 3) as geom2,
               st_buffer(ST_StartPoint(st_geometryn(ST_Split(geom_way, line_point), 1)), 0.000001) as geom1_start,
               st_buffer(ST_EndPoint(st_geometryn(ST_Split(geom_way, line_point), 1)), 0.000001) as geom1_end,
               ST_SetSRID(st_makepoint(x1, y1), 4326), source, target
        INTO geom1, geom2, geom1_start, geom1_end, geom_point, node_source, node_target
        FROM (
                 SELECT x1, y1, source, target, geom_way, st_buffer(ST_ClosestPoint(geom_way, poi), 0.000000001) As line_point
                 FROM (
                          select source, target, x1, y1, geom_way, ST_SetSRID(ST_MakePoint(x, y), 4326)::geometry as poi
                          from ie_edges
                          where flags & 1 != 0
                          order by geom_way <-> ST_SetSRID(ST_MakePoint(x, y), 4326)::geometry
                          limit 1
                      ) as al) as al2;

        if (select st_contains(geom1_start, geom_point)) or (select st_contains(geom1_end, geom_point)) then
            tgt := node_source;
            src := node_target;
            geom := geom1;
            return next;

            tgt := node_target;
            src := node_source;
            geom := geom2;
            return next;
        else
            tgt := node_target;
            src := node_source;
            geom := geom1;
            return next;

            tgt := node_source;
            src := node_target;
            geom := geom2;
            return next;
        end if;
end
$$ LANGUAGE plpgsql;