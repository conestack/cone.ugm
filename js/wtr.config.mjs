import {importMapsPlugin} from '@web/dev-server-import-maps';
import {playwrightLauncher} from '@web/test-runner-playwright';
import {defaultReporter, summaryReporter} from '@web/test-runner'

export const importMap = {
    imports: {
        'jquery': './node_modules/jquery/dist-module/jquery.module.js',
        'treibstoff': './sources/treibstoff/src/treibstoff.js',
        'cone': './js/tests/cone_stub.js',
    },
};

export default {
    nodeResolve: true,
    browsers: [
        playwrightLauncher({product: 'chromium'}),
    ],
    testFramework: {
        path: './node_modules/web-test-runner-qunit/dist/autorun.js',
        config: {
            noglobals: false
        }
    },
    files: [
        'js/tests/**/test_*.js'
    ],
    coverageConfig: {
        include: ['**/js/src/**/*.js'],
        exclude: ['**/node_modules/**', 'sources/**']
    },
    reporters: [defaultReporter(), summaryReporter({flatten: true})],
    plugins: [
        importMapsPlugin({
            inject: {importMap},
        }),
    ],
}
