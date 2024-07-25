import {type Reducer, useCallback, useReducer} from 'react';

import {parseFilterValueDate} from 'sentry/components/searchQueryBuilder/tokens/filter/parsers/date/parser';
import type {
  FieldDefinitionGetter,
  FocusOverride,
} from 'sentry/components/searchQueryBuilder/types';
import {
  isDateToken,
  makeTokenKey,
  parseQueryBuilderValue,
} from 'sentry/components/searchQueryBuilder/utils';
import {
  FilterType,
  type ParseResultToken,
  TermOperator,
  Token,
  type TokenResult,
} from 'sentry/components/searchSyntax/parser';
import {stringifyToken} from 'sentry/components/searchSyntax/utils';
import {MAX_QUERY_LENGTH} from 'sentry/constants';

type QueryBuilderState = {
  focusOverride: FocusOverride | null;
  query: string;
};

type ClearAction = {type: 'CLEAR'};

type UpdateQueryAction = {
  query: string;
  type: 'UPDATE_QUERY';
  focusOverride?: FocusOverride | null;
};

type ResetFocusOverrideAction = {type: 'RESET_FOCUS_OVERRIDE'};

type DeleteTokenAction = {
  token: ParseResultToken;
  type: 'DELETE_TOKEN';
};

type DeleteTokensAction = {
  tokens: ParseResultToken[];
  type: 'DELETE_TOKENS';
  focusOverride?: FocusOverride;
};

type UpdateFreeTextAction = {
  text: string;
  tokens: ParseResultToken[];
  type: 'UPDATE_FREE_TEXT';
  focusOverride?: FocusOverride;
};

type ReplaceTokensWithTextAction = {
  text: string;
  tokens: ParseResultToken[];
  type: 'REPLACE_TOKENS_WITH_TEXT';
};

type UpdateFilterOpAction = {
  op: TermOperator;
  token: TokenResult<Token.FILTER>;
  type: 'UPDATE_FILTER_OP';
};

type UpdateTokenValueAction = {
  token: TokenResult<Token.FILTER>;
  type: 'UPDATE_TOKEN_VALUE';
  value: string;
};

type MultiSelectFilterValueAction = {
  token: TokenResult<Token.FILTER>;
  type: 'TOGGLE_FILTER_VALUE';
  value: string;
};

type DeleteLastMultiSelectFilterValueAction = {
  token: TokenResult<Token.FILTER>;
  type: 'DELETE_LAST_MULTI_SELECT_FILTER_VALUE';
};

export type QueryBuilderActions =
  | ClearAction
  | UpdateQueryAction
  | ResetFocusOverrideAction
  | DeleteTokenAction
  | DeleteTokensAction
  | UpdateFreeTextAction
  | ReplaceTokensWithTextAction
  | UpdateFilterOpAction
  | UpdateTokenValueAction
  | MultiSelectFilterValueAction
  | DeleteLastMultiSelectFilterValueAction;

function truncateQuery(query: string): string {
  return query.slice(0, MAX_QUERY_LENGTH);
}

function removeQueryToken(query: string, token: TokenResult<Token>): string {
  return removeExcessWhitespaceFromParts(
    query.substring(0, token.location.start.offset),
    query.substring(token.location.end.offset)
  );
}

function removeQueryTokensFromQuery(
  query: string,
  tokens: Array<TokenResult<Token>>
): string {
  if (!tokens.length) {
    return query;
  }

  return removeExcessWhitespaceFromParts(
    query.substring(0, tokens[0].location.start.offset),
    query.substring(tokens.at(-1)!.location.end.offset)
  );
}

function deleteQueryTokens(
  state: QueryBuilderState,
  action: DeleteTokensAction
): QueryBuilderState {
  if (!action.tokens.length) {
    return state;
  }

  return {
    ...state,
    query: removeQueryTokensFromQuery(state.query, action.tokens),
    focusOverride: action.focusOverride ?? null,
  };
}

function modifyFilterOperator(
  query: string,
  token: TokenResult<Token.FILTER>,
  newOperator: TermOperator
): string {
  if (isDateToken(token)) {
    return modifyFilterOperatorDate(query, token, newOperator);
  }

  const isNotEqual = newOperator === TermOperator.NOT_EQUAL;

  const newToken: TokenResult<Token.FILTER> = {...token};
  newToken.operator = isNotEqual ? TermOperator.DEFAULT : newOperator;
  newToken.negated = isNotEqual;

  return replaceQueryToken(query, token, stringifyToken(newToken));
}

function modifyFilterOperatorDate(
  query: string,
  token: TokenResult<Token.FILTER>,
  newOperator: TermOperator
): string {
  switch (newOperator) {
    case TermOperator.GREATER_THAN:
    case TermOperator.LESS_THAN: {
      if (token.filter === FilterType.RELATIVE_DATE) {
        token.value.sign = newOperator === TermOperator.GREATER_THAN ? '-' : '+';
      } else if (
        token.filter === FilterType.SPECIFIC_DATE ||
        token.filter === FilterType.DATE
      ) {
        token.operator = newOperator;
      }
      return replaceQueryToken(query, token, stringifyToken(token));
    }

    // The "equal" and "or equal to" operators require a specific date
    case TermOperator.EQUAL:
    case TermOperator.GREATER_THAN_EQUAL:
    case TermOperator.LESS_THAN_EQUAL:
      // If it's a relative date, modify the operator and generate an ISO timestamp
      if (token.filter === FilterType.RELATIVE_DATE) {
        const generatedIsoDateStr = token.value.parsed?.value ?? new Date().toISOString();
        const newTokenStr = `${token.key.text}:${newOperator}${generatedIsoDateStr}`;
        return replaceQueryToken(query, token, newTokenStr);
      }
      token.operator = newOperator;
      return replaceQueryToken(query, token, stringifyToken(token));
    default:
      return replaceQueryToken(query, token, newOperator);
  }
}

function modifyFilterValueDate(
  query: string,
  token: TokenResult<Token.FILTER>,
  newValue: string
): string {
  const parsedValue = parseFilterValueDate(newValue);

  if (!parsedValue) {
    return query;
  }

  if (token.value.type === parsedValue?.type) {
    return replaceQueryToken(query, token.value, newValue);
  }

  if (parsedValue.type === Token.VALUE_ISO_8601_DATE) {
    if (token.value.type === Token.VALUE_RELATIVE_DATE) {
      if (token.value.sign === '-') {
        return replaceQueryToken(query, token.value, `>${newValue}`);
      }
      return replaceQueryToken(query, token.value, `<${newValue}`);
    }
    return replaceQueryToken(query, token.value, newValue);
  }

  return replaceQueryToken(query, token, `${token.key.text}:${newValue}`);
}

function replaceQueryTokens(
  query: string,
  tokens: TokenResult<Token>[],
  value: string
): string {
  if (tokens.length === 0) {
    return query;
  }

  const start = query.substring(0, tokens[0].location.start.offset);
  const end = query.substring(tokens.at(-1)!.location.end.offset);

  return start + value + end;
}

function replaceQueryToken(
  query: string,
  token: TokenResult<Token>,
  value: string
): string {
  return replaceQueryTokens(query, [token], value);
}

function removeExcessWhitespaceFromParts(...parts: string[]): string {
  return parts
    .map(part => part.trim())
    .filter(part => part.length > 0)
    .join(' ')
    .trim();
}

// Ensures that the replaced token is separated from the rest of the query
// and cleans up any extra whitespace
export function replaceTokensWithPadding(
  query: string,
  tokens: TokenResult<Token>[],
  value: string
): string {
  if (tokens.length === 0) {
    return query;
  }

  const start = query.substring(0, tokens[0].location.start.offset);
  const end = query.substring(tokens.at(-1)!.location.end.offset);

  return removeExcessWhitespaceFromParts(start, value, end);
}

function updateFreeText(
  state: QueryBuilderState,
  action: UpdateFreeTextAction
): QueryBuilderState {
  const newQuery = replaceTokensWithPadding(state.query, action.tokens, action.text);

  return {
    ...state,
    query: truncateQuery(newQuery),
    focusOverride:
      action.focusOverride === undefined ? state.focusOverride : action.focusOverride,
  };
}

function replaceTokensWithText(
  state: QueryBuilderState,
  action: ReplaceTokensWithTextAction,
  getFieldDefinition: FieldDefinitionGetter
): QueryBuilderState {
  const newQuery = replaceTokensWithPadding(state.query, action.tokens, action.text);
  const cursorPosition =
    (action.tokens[0]?.location.start.offset ?? 0) + action.text.length;
  const newParsedQuery = parseQueryBuilderValue(newQuery, getFieldDefinition);
  const focusedToken = newParsedQuery?.find(
    token => token.type === Token.FREE_TEXT && token.location.end.offset >= cursorPosition
  );

  const focusedItemKey = focusedToken ? makeTokenKey(focusedToken, newParsedQuery) : null;

  return {
    ...state,
    query: truncateQuery(newQuery),
    focusOverride: focusedItemKey ? {itemKey: focusedItemKey} : null,
  };
}

function modifyFilterValue(
  query: string,
  token: TokenResult<Token.FILTER>,
  newValue: string
): string {
  if (isDateToken(token)) {
    return modifyFilterValueDate(query, token, newValue);
  }

  return replaceQueryToken(query, token.value, newValue);
}

function updateFilterMultipleValues(
  state: QueryBuilderState,
  token: TokenResult<Token.FILTER>,
  values: string[]
) {
  const uniqNonEmptyValues = Array.from(
    new Set(values.filter(value => value.length > 0))
  );
  if (uniqNonEmptyValues.length === 0) {
    return {
      ...state,
      query: truncateQuery(replaceQueryToken(state.query, token.value, '""')),
    };
  }

  const newValue =
    uniqNonEmptyValues.length > 1
      ? `[${uniqNonEmptyValues.join(',')}]`
      : uniqNonEmptyValues[0];

  return {
    ...state,
    query: truncateQuery(replaceQueryToken(state.query, token.value, newValue)),
  };
}

function multiSelectTokenValue(
  state: QueryBuilderState,
  action: MultiSelectFilterValueAction
) {
  const tokenValue = action.token.value;

  switch (tokenValue.type) {
    case Token.VALUE_TEXT_LIST:
    case Token.VALUE_NUMBER_LIST:
      const values = tokenValue.items.map(item => item.value?.text ?? '');
      const containsValue = values.includes(action.value);
      const newValues = containsValue
        ? values.filter(value => value !== action.value)
        : [...values, action.value];

      return updateFilterMultipleValues(state, action.token, newValues);
    default:
      if (tokenValue.text === action.value) {
        return updateFilterMultipleValues(state, action.token, ['']);
      }
      const newValue = tokenValue.value
        ? [tokenValue.text, action.value]
        : [action.value];
      return updateFilterMultipleValues(state, action.token, newValue);
  }
}

function deleteLastMultiSelectTokenValue(
  state: QueryBuilderState,
  action: DeleteLastMultiSelectFilterValueAction
) {
  const tokenValue = action.token.value;

  switch (tokenValue.type) {
    case Token.VALUE_TEXT_LIST:
    case Token.VALUE_NUMBER_LIST:
      const newValues = tokenValue.items.slice(0, -1).map(item => item.value?.text ?? '');

      return updateFilterMultipleValues(state, action.token, newValues);
    default:
      return updateFilterMultipleValues(state, action.token, ['']);
  }
}

export function useQueryBuilderState({
  initialQuery,
  getFieldDefinition,
  disabled,
}: {
  disabled: boolean;
  getFieldDefinition: FieldDefinitionGetter;
  initialQuery: string;
}) {
  const initialState: QueryBuilderState = {query: initialQuery, focusOverride: null};

  const reducer: Reducer<QueryBuilderState, QueryBuilderActions> = useCallback(
    (state, action): QueryBuilderState => {
      if (disabled) {
        return state;
      }

      switch (action.type) {
        case 'CLEAR':
          return {
            ...state,
            query: '',
            focusOverride: {
              itemKey: `${Token.FREE_TEXT}:0`,
            },
          };
        case 'UPDATE_QUERY':
          return {
            ...state,
            query: truncateQuery(action.query),
            focusOverride: action.focusOverride ?? null,
          };
        case 'RESET_FOCUS_OVERRIDE':
          return {
            ...state,
            focusOverride: null,
          };
        case 'DELETE_TOKEN':
          return {
            ...state,
            query: truncateQuery(removeQueryToken(state.query, action.token)),
          };
        case 'DELETE_TOKENS':
          return deleteQueryTokens(state, action);
        case 'UPDATE_FREE_TEXT':
          return updateFreeText(state, action);
        case 'REPLACE_TOKENS_WITH_TEXT':
          return replaceTokensWithText(state, action, getFieldDefinition);
        case 'UPDATE_FILTER_OP':
          return {
            ...state,
            query: truncateQuery(
              modifyFilterOperator(state.query, action.token, action.op)
            ),
          };
        case 'UPDATE_TOKEN_VALUE':
          return {
            ...state,
            query: truncateQuery(
              modifyFilterValue(state.query, action.token, action.value)
            ),
          };
        case 'TOGGLE_FILTER_VALUE':
          return multiSelectTokenValue(state, action);
        case 'DELETE_LAST_MULTI_SELECT_FILTER_VALUE':
          return deleteLastMultiSelectTokenValue(state, action);
        default:
          return state;
      }
    },
    [disabled, getFieldDefinition]
  );

  const [state, dispatch] = useReducer(reducer, initialState);

  return {
    state,
    dispatch,
  };
}
