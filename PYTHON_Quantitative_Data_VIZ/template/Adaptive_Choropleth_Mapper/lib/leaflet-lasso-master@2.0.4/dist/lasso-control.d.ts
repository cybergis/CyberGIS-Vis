import L from 'leaflet';
import { LassoHandlerOptions } from './lasso-handler';
import './lasso-control.css';
export declare type LassoControlOptions = LassoHandlerOptions & L.ControlOptions;
export declare class LassoControl extends L.Control {
    options: LassoControlOptions;
    private lasso?;
    constructor(options?: LassoControlOptions);
    setOptions(options: LassoControlOptions): void;
    onAdd(map: L.Map): HTMLDivElement;
    enabled(): boolean;
    enable(): void;
    disable(): void;
    toggle(): void;
}