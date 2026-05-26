import {NextIntlClientProvider} from 'next-intl';
import {getMessages} from 'next-intl/server';
import Sidebar from '@/components/Sidebar';

export default async function LocaleLayout({
  children,
  params
}: {
  children: React.ReactNode;
  params: Promise<{locale: string}>;
}) {
  const {locale} = await params;
  const messages = await getMessages();

  return (
    <NextIntlClientProvider messages={messages}>
      <div className="flex min-h-screen">
        <Sidebar locale={locale} />
        <main className="flex-1 overflow-y-auto p-4 md:p-8">
          {children}
        </main>
      </div>
    </NextIntlClientProvider>
  );
}
