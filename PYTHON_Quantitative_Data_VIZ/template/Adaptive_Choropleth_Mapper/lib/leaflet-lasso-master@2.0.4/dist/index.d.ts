import { LassoHandler } from './lasso-handler';
import { LassoControl } from './lasso-control';
declare module 'leaflet' {
    type Lasso = LassoHandler;
    let Lasso: typeof LassoHandler;
    let lasso: (...args: ConstructorParameters<typeof LassoHandler>) => LassoHandler;
    namespace Control {
        type Lasso = LassoControl;
        let Lasso: typeof LassoControl;
    }
    namespace control {
        let lasso: (...args: ConstructorParameters<typeof LassoControl>) => LassoControl;
    }
}
export * from './lasso-handler';
export * from './lasso-control';