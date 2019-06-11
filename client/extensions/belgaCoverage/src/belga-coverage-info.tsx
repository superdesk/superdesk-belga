import * as React from 'react';

import {ISuperdesk} from 'superdesk-api';
import {IBelgaCoverage, getCoverageInfo} from './belga-image-api';

interface IProps {
    coverageId: string;
    removeCoverage?: () => void;
    superdesk: ISuperdesk;
}

interface IState {
    loading: boolean;
    coverage: IBelgaCoverage | null;
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
        const {Alert, Figure} = this.props.superdesk.components;

        if (this.state.loading) {
            return null;
        }

        if (this.state.coverage === null) {
            return <Alert type="error">{'There was an error when fetching coverage.'}</Alert>;
        }

        // workaround for this.state.coverage can be null
        const coverage: IBelgaCoverage = this.state.coverage!;

        return (
            <Figure caption={coverage.description}
                onRemove={this.props.removeCoverage}>
                <img src={coverage.iconThumbnailUrl} />
            </Figure>
        );
    }
}
