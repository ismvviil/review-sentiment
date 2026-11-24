/** Joins truthy class names: cx('a', cond && 'b') -> 'a b'. */
export const cx = (...classes: (string | false | null | undefined)[]): string =>
  classes.filter(Boolean).join(' ')
