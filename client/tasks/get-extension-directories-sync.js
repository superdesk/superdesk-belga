/* eslint-disable comma-dangle */

var fs = require('fs');
var path = require('path');
var lstatSync = fs.lstatSync;

var flatMap = require('lodash/flatMap');

function getExtensionDirectoriesSync() {
    return flatMap([
        '../extensions',
    ], (relativePath) => {
        const absolutePath = path.resolve(__dirname + '/' + relativePath);

        return (fs.existsSync(absolutePath) ? fs.readdirSync(absolutePath) : [])
            .map((extensionName) => ({extensionName, relativePath, absolutePath}))
            .filter(
                ({absolutePath, extensionName}) => lstatSync(absolutePath + '/' + extensionName).isDirectory()
            );
    });
}

module.exports = getExtensionDirectoriesSync;