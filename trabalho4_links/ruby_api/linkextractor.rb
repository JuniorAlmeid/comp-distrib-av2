require 'sinatra'
require 'open-uri'
require 'nokogiri'
require 'json'
require 'redis'

set :bind, '0.0.0.0'
set :port, 5000

redis_url = ENV['REDIS_URL']
cache = (redis_url && !redis_url.empty?) ? Redis.new(url: redis_url) : nil

get '/api/links' do
  url = params['url']
  if cache
    begin
      cached = cache.get(url)
      return cached if cached
    rescue
    end
  end
  begin
    doc = Nokogiri::HTML(URI.open(url, "User-Agent" => "Mozilla/5.0", :read_timeout => 10))
    links = doc.css('a').map { |a| a['href'] }.compact
    result = { url: url, links: links }.to_json
    if cache
      begin cache.setex(url, 300, result) rescue nil end
    end
    content_type :json
    result
  rescue => e
    status 400
    { error: e.message }.to_json
  end
end
