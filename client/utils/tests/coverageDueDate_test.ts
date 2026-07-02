import moment from 'moment-timezone';
import {getEventDateContext, getCoverageDueDate} from '../coverageDueDate';

jest.mock('superdesk-planning/client/utils', () => ({
    eventUtils: {
        isEventAllDay: (start: moment.Moment, end: moment.Moment) =>
            start.hour() === 0 && start.minute() === 0 &&
            end.hour() === 23 && end.minute() === 59,
    },
    timeUtils: {
        getDateInRemoteTimeZone: (date: moment.MomentInput, tz: string) =>
            moment.tz(date, tz),
        localTimeZone: () => 'UTC',
    },
}));

interface TimezoneCase {
    name: string;
    tz: string;
}

const timezones: TimezoneCase[] = [
    {name: 'Toronto', tz: 'America/Toronto'},
    {name: 'Prague', tz: 'Europe/Prague'},
    {name: 'Tokyo', tz: 'Asia/Tokyo'},
];

// Helper to create UTC timestamps that map to specific local times
const utc = (localTime: string, tz: string) =>
    moment.tz(localTime, tz).utc().format();

describe('coverageDueDate', () => {
    it.each(timezones)('sets all-day event to 20:00 on the event day in $name timezone', ({tz}) => {
        const event: any = {
            dates: {
                start: utc('2026-07-01T00:00:00', tz),
                end: utc('2026-07-01T23:59:00', tz),
                tz,
                all_day: true,
            },
        };
        const planning: any = {planning_date: utc('2026-07-01T00:00:00', tz)};

        const result = getCoverageDueDate(planning, event);

        expect(result?.format()).toBe(moment.tz('2026-07-01T20:00:00', tz).format());
    });

    it.each(timezones)('sets TBC event to 20:00 on the event day in $name timezone', ({tz}) => {
        const event: any = {
            dates: {
                start: utc('2026-07-01T10:00:00', tz),
                end: utc('2026-07-01T18:00:00', tz),
                tz,
            },
            _time_to_be_confirmed: true,
        };
        const planning: any = {planning_date: utc('2026-07-01T00:00:00', tz)};

        const result = getCoverageDueDate(planning, event);

        expect(result?.format()).toBe(moment.tz('2026-07-01T20:00:00', tz).format());
    });

    it.each(timezones)('sets timed event to end + 1 hour on the same day in $name timezone', ({tz}) => {
        const event: any = {
            dates: {
                start: utc('2026-07-01T14:00:00', tz),
                end: utc('2026-07-01T18:00:00', tz),
                tz,
            },
        };
        const planning: any = {planning_date: utc('2026-07-01T00:00:00', tz)};

        const result = getCoverageDueDate(planning, event);

        expect(result?.format()).toBe(moment.tz('2026-07-01T19:00:00', tz).format());
    });

    it.each(timezones)('falls back to planning_date when event dates are missing in $name timezone', ({tz}) => {
        const event: any = {dates: {tz}};
        const planning: any = {planning_date: moment.tz('2026-07-01T12:00:00Z', 'UTC')};

        const {start, end} = getEventDateContext(event, planning);

        expect(start.format()).toBe(moment.tz('2026-07-01T12:00:00Z', 'UTC').format());
        expect(end.format()).toBe(moment.tz('2026-07-01T12:00:00Z', 'UTC').format());
    });
});
