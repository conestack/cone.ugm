import cleanup from 'rollup-plugin-cleanup';
import {terser} from 'rollup-plugin-terser';

const out_dir = 'src/cone/ugm/browser/static';

const outro = `
window.ugm = exports;
`;

export default args => {
    let conf = {
        input: 'js/src/bundle.js',
        plugins: [
            cleanup()
        ],
        output: [{
            file: `${out_dir}/cone.ugm.js`,
            name: 'cone_ugm',
            format: 'iife',
            outro: outro,
            globals: {
                jquery: 'jQuery',
                treibstoff: 'treibstoff',
                cone: 'cone'
            },
            interop: 'default',
            sourcemap: true,
            sourcemapExcludeSources: true
        }],
        external: [
            'jquery',
            'treibstoff',
            'cone'
        ]
    };
    if (args.configDebug !== true) {
        conf.output.push({
            file: `${out_dir}/cone.ugm.min.js`,
            name: 'cone_ugm',
            format: 'iife',
            plugins: [
                terser()
            ],
            outro: outro,
            globals: {
                jquery: 'jQuery',
                treibstoff: 'treibstoff',
                cone: 'cone'
            },
            interop: 'default',
            sourcemap: true,
            sourcemapExcludeSources: true
        });
    }
    return conf;
};
