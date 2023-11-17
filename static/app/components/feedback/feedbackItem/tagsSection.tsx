import ErrorBoundary from 'sentry/components/errorBoundary';
import Section from 'sentry/components/feedback/feedbackItem/feedbackItemSection';
import {KeyValueTable, KeyValueTableRow} from 'sentry/components/keyValueTable';
import TextOverflow from 'sentry/components/textOverflow';
import {Tooltip} from 'sentry/components/tooltip';
import {IconTag} from 'sentry/icons';
import {t} from 'sentry/locale';

interface Props {
  tags: Record<string, string>;
}

export default function TagsSection({tags}: Props) {
  const entries = Object.entries(tags);
  if (!entries.length) {
    return null;
  }

  return (
    <Section icon={<IconTag size="xs" />} title={t('Tags')}>
      <ErrorBoundary mini>
        <KeyValueTable noMargin>
          {entries.map(([key, value]) => (
            <KeyValueTableRow
              key={key}
              keyName={key}
              value={
                <Tooltip showOnlyOnOverflow title={value}>
                  <TextOverflow>{value}</TextOverflow>
                </Tooltip>
              }
            />
          ))}
        </KeyValueTable>
      </ErrorBoundary>
    </Section>
  );
}
