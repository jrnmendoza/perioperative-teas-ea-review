#!/usr/bin/env ruby

require "base64"
require "csv"
require "json"
require "tempfile"
require "time"

path, mode, encoded_payload = ARGV
abort "usage: audit_csv_writer.rb PATH MODE BASE64_JSON" unless path && mode && encoded_payload

payload_json = encoded_payload == "-" ? STDIN.read : Base64.strict_decode64(encoded_payload)
payload = JSON.parse(payload_json)
table = CSV.read(path, headers: true)
headers = table.headers
rows = table.map(&:to_h)

abort "missing or duplicate CSV headers" unless headers.compact.uniq.length == headers.length
abort "existing malformed CSV row" unless table.none? { |row| row[nil] }

case mode
when "append"
  abort "payload fields differ from CSV schema" unless payload.keys.sort == headers.sort
  abort "invalid decision" unless %w[Yes Maybe No].include?(payload.fetch("decision_yes_maybe_no"))
  abort "new row must start unregistered" unless payload.fetch("vote_registered_yes_no") == "no"
  abort "new row timestamp must be empty" unless payload.fetch("post_vote_timestamp").to_s.empty?
  abort "duplicate screening sequence" if rows.any? { |row| row["screening_sequence"] == payload["screening_sequence"] }
  abort "duplicate Covidence number" if rows.any? { |row| row["covidence_number"] == payload["covidence_number"] }
  rows << headers.to_h { |header| [header, payload.fetch(header).to_s] }
when "register"
  required = %w[screening_sequence covidence_number post_vote_timestamp]
  abort "register payload fields invalid" unless payload.keys.sort == required.sort
  Time.iso8601(payload.fetch("post_vote_timestamp"))
  matches = rows.select do |row|
    row["screening_sequence"] == payload["screening_sequence"] &&
      row["covidence_number"] == payload["covidence_number"]
  end
  abort "registration target is not unique" unless matches.length == 1
  row = matches.first
  abort "registration target is not pending" unless row["vote_registered_yes_no"] == "no"
  abort "registration target already has timestamp" unless row["post_vote_timestamp"].to_s.empty?
  row["vote_registered_yes_no"] = "yes"
  row["post_vote_timestamp"] = payload.fetch("post_vote_timestamp")
else
  abort "unsupported mode"
end

Tempfile.create(["screening-decisions-", ".csv"], File.dirname(path)) do |temp|
  CSV.open(temp.path, "wb", write_headers: true, headers: headers) do |csv|
    rows.each { |row| csv << headers.map { |header| row.fetch(header, "") } }
  end
  temp.flush
  temp.fsync
  File.rename(temp.path, path)
end

verified = CSV.read(path, headers: true)
abort "written row count mismatch" unless verified.length == rows.length
abort "written malformed CSV row" unless verified.none? { |row| row[nil] }
abort "written field-count mismatch" unless verified.all? { |row| row.fields.length == headers.length }
abort "duplicate written screening sequence" unless verified.map { |row| row["screening_sequence"] }.uniq.length == verified.length
abort "duplicate written Covidence number" unless verified.map { |row| row["covidence_number"] }.uniq.length == verified.length

puts JSON.generate(
  rows: verified.length,
  registered: verified.count { |row| row["vote_registered_yes_no"] == "yes" },
  pending: verified.count { |row| row["vote_registered_yes_no"] == "no" },
  last_sequence: verified[-1]["screening_sequence"],
  last_covidence_number: verified[-1]["covidence_number"]
)
