FROM ruby:3.1-alpine
RUN apk add --no-cache build-base patch zlib-dev libxml2-dev libxslt-dev
WORKDIR /app
COPY Gemfile .
RUN bundle install
COPY linkextractor.rb .
CMD ["ruby", "linkextractor.rb"]
