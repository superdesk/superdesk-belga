import moment from 'moment-timezone';
import {IEventItem, IPlanningItem} from 'superdesk-planning/client/interfaces';
import {eventUtils, timeUtils} from 'superdesk-planning/client/utils';

const ALL_DAY_DUE_HOUR = 20;

/**
 * All-day Events store their day as a UTC date, so take the day from UTC
 * and set the due time on that day in the Event's timezone
 */
const getAllDayDueDate = (eventItem: IEventItem): moment.Moment => {
    const day = moment.utc(eventItem.dates.end ?? eventItem.dates.start).format('YYYY-MM-DD');
    const dueDate = `${day}T${ALL_DAY_DUE_HOUR}:00:00`;

    return eventItem.dates.tz ? moment.tz(dueDate, eventItem.dates.tz) : moment(dueDate);
};

export const getEventDateContext = (eventItem?: IEventItem, planningItem?: IPlanningItem) => {
    const tz = eventItem?.dates?.tz;
    const fallback = moment(planningItem?.planning_date);

    const toEventTz = (value?: moment.MomentInput) =>
        value && tz ? timeUtils.getDateInRemoteTimeZone(value as moment.Moment, tz) : fallback.clone();

    const start = toEventTz(eventItem?.dates?.start);
    const end = toEventTz(eventItem?.dates?.end);

    const isAllDay =
        !!eventItem?.dates?.all_day ||
        (!!eventItem?.dates?.start &&
            !!eventItem?.dates?.end &&
            eventUtils.isEventAllDay({
                ...eventItem,
                dates: {...eventItem.dates, start, end},
            }));

    return {start, end, isAllDay};
};

export const getCoverageDueDate = (
    planningItem: IPlanningItem,
    eventItem?: IEventItem,
): moment.Moment | null => {
    const {end, isAllDay} = getEventDateContext(eventItem, planningItem);
    let coverageTime: moment.Moment | null = null;

    if (eventItem?.dates?.all_day === true && (eventItem.dates.end ?? eventItem.dates.start) != null) {
        coverageTime = getAllDayDueDate(eventItem);
    } else if (eventItem && isAllDay) {
        coverageTime = end.clone();
        coverageTime.set('hour', ALL_DAY_DUE_HOUR);
        coverageTime.set('minute', 0);
        coverageTime.set('second', 0);
    } else if (eventItem && eventItem._time_to_be_confirmed) {
        coverageTime = end.clone();
        coverageTime.set('hour', ALL_DAY_DUE_HOUR);
        coverageTime.set('minute', 0);
        coverageTime.set('second', 0);
    } else if (eventItem) {
        coverageTime = end.clone();
        coverageTime.add(1, 'hour');
        if (!coverageTime.isSame(end, 'day')) {
            // make sure we're not going into the next day
            coverageTime = end.clone();
        }
    } else if (planningItem) {
        coverageTime = moment(planningItem.planning_date);
    }

    return coverageTime;
};
