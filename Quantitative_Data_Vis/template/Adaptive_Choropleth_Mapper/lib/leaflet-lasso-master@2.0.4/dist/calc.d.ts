import L from 'leaflet';
export declare function getLayersInPolygon(polygon: GeoJSON.Polygon, layers: L.Layer[], options?: {
    zoom?: number;
    crs?: L.CRS;
    intersect?: boolean;
}): L.Layer[];