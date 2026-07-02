module.exports = {
    preset: 'ts-jest',
    testEnvironment: 'node',
    roots: ['<rootDir>'],
    testMatch: ['**/*_test.ts?(x)'],
    moduleNameMapper: {
        '^superdesk-planning/(.*)$': '<rootDir>/node_modules/superdesk-planning/$1',
        '^superdesk-core/(.*)$': '<rootDir>/node_modules/superdesk-core/$1',
    },
    transform: {
        '^.+\\.tsx?$': ['ts-jest', {
            tsconfig: {
                esModuleInterop: true,
                allowSyntheticDefaultImports: true,
            },
        }],
    },
};
