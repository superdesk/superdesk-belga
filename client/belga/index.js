import angular from 'angular';

import belgaImage from './image';
import belga360Archive from './360archive';

export default angular.module('belga', [
    belgaImage.name,
    belga360Archive.name,
]);
