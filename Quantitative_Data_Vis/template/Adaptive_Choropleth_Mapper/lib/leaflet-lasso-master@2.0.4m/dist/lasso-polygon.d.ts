import L from 'leaflet';
export declare class LassoPolygon extends L.Layer {
    readonly polyline: L.Polyline;
    readonly polygon: L.Polygon;
    constructor(latlngs: L.LatLngExpression[], options?: L.PolylineOptions);
    onAdd(map: L.Map): this;
    onRemove(): this;
    addLatLng(latlng: L.LatLngExpression): this;
    getLatLngs(): L.LatLng[];
    toGeoJSON(): GeoJSON.Feature<GeoJSON.Polygon>;
}