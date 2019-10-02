import {ISuperdesk, IExtension, IExtensionActivationResult} from 'superdesk-api';
import { getActionsBulkInitialize } from "./get-article-actions-bulk";

const extension: IExtension = {
    activate: (superdesk: ISuperdesk) => {
        const result: IExtensionActivationResult = {
            contributions: {
                entities: {
                    article: {
                        getActionsBulk: getActionsBulkInitialize(superdesk),
                    }
                }
            }

        };

        return Promise.resolve(result);
    },
};

export default extension;
