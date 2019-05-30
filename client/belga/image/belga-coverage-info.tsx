import React from 'react';

import {Alert} from 'superdesk-core/scripts/core/ui/components/alert';
import {Figure} from 'superdesk-core/scripts/core/ui/components/figure';

import {IBelgaCoverage, getCoverageInfo} from './belga-image-api';

interface IProps {
    coverageId: string;
    removeCoverage?: () => void;
}

interface IState {
    loading: boolean;
    coverage: IBelgaCoverage;
}

export default class BelgaCoverageAssocation extends React.Component<IProps, IState> {
    readonly state = {loading: true, coverage: null};

    componentDidMount() {
        this.fetchCoverage();
    }

    fetchCoverage() {
        getCoverageInfo(this.props.coverageId)
            .then((coverage) => this.setState({coverage: coverage, loading: false}))
            .catch(() => {
                this.setState({loading: false});
            });
    }

    render() {
        if (this.state.loading) {
            return null;
        }

        if (this.state.coverage == null) {
            return <Alert type="error">{'There was an error when fetching coverage.'}</Alert>;
        }

        return (
            <Figure caption={this.state.coverage.description}
                onRemove={this.props.removeCoverage}>
                <img src={this.state.coverage.iconThumbnailUrl} />
            </Figure>
        );
    }
}
