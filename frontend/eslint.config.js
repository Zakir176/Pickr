import js from '@eslint/js';
import pluginVue from 'eslint-plugin-vue';
import globals from 'globals';

export default [
    js.configs.recommended,
    ...pluginVue.configs['flat/recommended'],
    {
        ignores: ['dist/**', 'node_modules/**', 'dev-dist/**']
    },
    {
        files: ['*.vue', '**/*.vue', '*.js', '**/*.js'],
        languageOptions: {
            ecmaVersion: 'latest',
            sourceType: 'module',
            globals: {
                ...globals.browser,
                ...globals.node,
                ...globals.es2021,
                process: 'readonly'
            }
        },
        rules: {
            'vue/multi-word-component-names': 'off',
            'no-unused-vars': 'warn',
            'vue/no-unused-vars': 'warn',
            'no-console': 'off'
        }
    }
];
