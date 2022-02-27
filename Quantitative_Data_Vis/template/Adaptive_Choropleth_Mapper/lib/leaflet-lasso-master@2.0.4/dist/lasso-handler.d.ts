import L from 'leaflet';
import { LassoPolygon } from './lasso-polygon';
import './lasso-handler.css';
export interface LassoHandlerOptions {
    polygon?: L.PolylineOptions;
    intersect?: boolean;
}
interface LassoHandlerFinishedEventData {
    latLngs: L.LatLng[];
    layers: L.Layer[];
}
export declare type LassoHandlerFinishedEvent = L.LeafletEvent & LassoHandlerFinishedEventData;
export declare const ENABLED_EVENT = "lasso.enabled";
export declare const DISABLED_EVENT = "lasso.disabled";
export declare const FINISHED_EVENT = "lasso.finished";
export declare const ACTIVE_CLASS = "leaflet-lasso-active";
export declare class LassoHandler extends L.Handler {
    options: LassoHandlerOptions;
    private map;
    private polygon?;
    private onDocumentMouseMoveBound;
    private onDocumentMouseUpBound;
    constructor(map: L.Map, options?: LassoHandlerOptions);
    setOptions(options: LassoHandlerOptions): void;
    toggle(): void;
    addHooks(): void;
    removeHooks(): void;
    getPolygon(): LassoPolygon | undefined;
    private onMapMouseDown;
    private onDocumentMouseMove;
    private onDocumentMouseUp;
    private finish;
}
export {};