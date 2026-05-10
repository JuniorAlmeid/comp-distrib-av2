FROM ruby:2.6-alpine
RUN apk add --no-cache build-base patch zlib-dev libxml2-dev libxslt-dev
WORKDIR /app
COPY Gemfile .
RUN bundle install
COPY linkextractor.rb .
CMD ["ruby", "linkextractor.rb", "-o", "0.0.0.0"]