import { ref } from 'vue';

type UseDrawerOption = {
  name: string;
  title: string;
  beforeOpen?: (row: any) => void;
  afterClose?: () => void;
};

export function useDrawer(options: UseDrawerOption[]) {
  const show = ref(false);
  const title = ref('');
  const name = ref('');
  const _options = options;

  // console.log('useDrawer', options);

  function open(_name: string, row: any) {
    const opt = _options.find((option) => option.name === _name);
    name.value = _name;
    title.value = opt?.title || '';
    opt?.beforeOpen?.(row);
    show.value = true;
    console.log('open', _name, opt);
  }

  // function close() {
  //   const opt = _options.find((option) => option.name === name.value);
  //   show.value = false;
  //   opt?.afterClose?.();
  // }
  // 修改close函数，增加force参数，默认值为true
  function close(force: boolean = true) {
    // 如果force为false，表示不强制关闭，可以在这里添加判断逻辑
    // 例如，提交失败时，可以调用close(false)来阻止抽屉关闭
    if (!force) {
      return; // 如果不是强制关闭，则直接返回，不执行关闭操作
    }
    const opt = _options.find((option) => option.name === name.value);
    show.value = false;
    opt?.afterClose?.();
  }

  return { show, title, name, open, close };
}
